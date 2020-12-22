#!/usr/bin/env python3
import asyncio
from datetime import timedelta
import pathlib
import sys
import os
from typing import List

from yapapi import (
    Executor,
    Task,
    __version__ as yapapi_version,
    WorkContext,
    windows_event_loop_fix,
)
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm
from yapapi.rest.activity import BatchTimeoutError

script_dir = pathlib.Path(__file__).resolve().parent
lib_dir = script_dir / "lib"
sys.path.append(str(lib_dir))

import text_colors
import argument_parser
from app import App
from batch import Batch
from run_times import RunTimes
from test_list import (Test, TestList)

async def main(subnet_tag: str, app: App, batches: List[Batch]):
    package = await vm.repo(
        # using existing image for 'blender' example
        image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
        min_mem_gib=1.0,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        cwd = pathlib.Path.cwd()
        async for task in tasks:
            batch = task.data
            try:
                os.remove(batch.local_out(cwd))
            except:
                pass

            for exe in batch.all_executables():            
                ctx.send_file(batch.local_exe(cwd, exe), batch.remote_exe(exe))
            batch.make_local_sh(cwd)
            ctx.send_file(batch.local_sh(cwd), batch.remote_sh())
            ctx.run("/bin/bash", batch.remote_sh())
            ctx.download_file(batch.remote_out(), batch.local_out(cwd))
            try:
                yield ctx.commit(timeout=timedelta(seconds=batch.timeout()))
                task.accept_result(result=batch.local_out(cwd))
            except BatchTimeoutError:
                print(
                    f"{text_colors.RED}"
                    f"Task timed out: {task.data.id}, time: {task.running_time}"
                    f"{text_colors.DEFAULT}"
                )
                raise

            
    # Worst-case overhead, in minutes, for initialization (negotiation, file transfer etc.)
    timeout = timedelta(minutes=app.args.time_out)

    # By passing `event_consumer=log_summary()` we enable summary logging.
    # See the documentation of the `yapapi.log` module on how to set
    # the level of detail and format of the logged information.
    async with Executor(
        package=package,
        max_workers=len(batches),
        budget=10.0,
        timeout=timeout,
        subnet_tag=subnet_tag,
        event_consumer=log_summary(log_event_repr),
    ) as executor:

        async for task in executor.submit(worker, [Task(data=batch) for batch in batches]):
            print(
                f"{text_colors.CYAN}"
                f"Task computed: {task.data.id}, result: {task.result}, time: {task.running_time}"
                f"{text_colors.DEFAULT}"
            ) 


if __name__ == "__main__":
    parser = argument_parser.build_parser("Run cargo test")
    dry_run = False
    parser.set_defaults(log_file="golem-cargo-test-yapapi.log")
    args = parser.parse_args()
    app = App(args)
    test_list_txt_file = app.execute_cargo_tst_with_list_option_to_get_the_list_of_all_tests()
    test_list = app.parse_test_list(test_list_txt_file)
    previous_run_times = RunTimes.from_file()
    if previous_run_times:
        test_list.update_runtimes(previous_run_times)
    batches = app.make_test_batches(test_list)

    print("batches: ", [b.total_duration() for b in batches])

    windows_event_loop_fix()
    enable_default_logger(log_file=args.log_file)

    if not dry_run:
        loop = asyncio.get_event_loop()
        subnet = args.subnet_tag
        sys.stderr.write(
            f"yapapi version: {text_colors.YELLOW}{yapapi_version}{text_colors.DEFAULT}\n"
        )
        sys.stderr.write(f"Using subnet: {text_colors.YELLOW}{subnet}{text_colors.DEFAULT}\n")
        task = loop.create_task(main(subnet_tag=args.subnet_tag, app=app, batches=batches))
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            print(
                f"{text_colors.YELLOW}"
                "Shutting down gracefully, please wait a short while "
                "or press Ctrl+C to exit immediately..."
                f"{text_colors.DEFAULT}"
            )
            task.cancel()
            try:
                loop.run_until_complete(task)
                print(
                    f"{text_colors.YELLOW}"
                    "Shutdown completed, thank you for waiting!"
                    f"{text_colors.DEFAULT}"
                )
            except (asyncio.CancelledError, KeyboardInterrupt):
                pass

    cwd = pathlib.Path.cwd()
    for b in batches:
        app.parse_output_file(b.local_out(cwd), test_list)
    run_times = RunTimes.from_run(test_list)
    run_times.save()
    print(f"\n\n\nTest summary: {app.compute_summary(test_list)}")
    app.concatenate_output(cwd, batches)
