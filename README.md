% golem_cargo_test
% Ladislav Sladecek (ladislav.sladecek@gmail.com)
% 2021-01-03

# Purpose

*golem_cargo_test* is an adaptive distributed test executor for *rust*
projects running on the *Golem* network.

The executor will split all the tests of a project into batches to
execute them in parallel on the *Golem* network. After all batches are
finished a test summary is printed to the console and a detailed test
log is saved to a text file. Moreover, a run-time statistics is
collected to improve batch distribution in the next run.

The user specifies required test duration on the command line using the
`--plan` argument. For example

```
golem_cargo_test --plan=300
```

means, that the executor will use as many parallel task as to achieve
total duration 300 seconds. For example, if total execution time of
all the tests in a project is 75 minutes, there will be 15 parallel
tasks running.



# Motivation

Each relevant software projects contains a battery of tests. If the
project implements computational algorithms, the tests are usually
extensive and need tens of minutes or even hours to execute. Typical
examples are project in contemporary cryptography, such as
zero-knowledge language 'Zokrates' https://zokrates.github.io/, or
implementations of 'Plonk' https://github.com/dusk-network/plonk and
'Groth16' https://github.com/arkworks-rs/groth16 protocols.

A developer is usually executing only the test for the feature they
are working on. After the work is finished, before software release,
they must execute the whole test set to make sure that nothing has
been spoiled by accident. This takes long time to complete.

With the *Golem* network and *golem_cargo_test* executor, the
developer can run several tests in parallel on several hired machines
to speed-up the release process significantly.

# Installation

This installation instructions are valid for `Linux` operating system
such as `Debian`. For other environments must be modified accordingly.

## *Golem* network

1 Install `yagna` daemon according to https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development

2 Initialize payments

3 Install `python3` module `yapapi`
```
python3 -m venv ~/.envs/yagna-python-tutorial
source ~/.envs/yagna-python-tutorial/bin/activate
```

4 Download software from `GitHub`
```
cd
git clone https://github.com/sladecek/golem_cargo_test
```

5 Add the script directory to the `PATH` environment variable.

## *Goth* test network

1 Install and execute `goth` according to https://www.youtube.com/watch?v=HP6VVBUdkm8

2 Install `python3` module `yapapi`
```
python3 -m venv ~/.envs/yagna-python-tutorial
source ~/.envs/yagna-python-tutorial/bin/activate
```

3 Download software from `GitHub`
```
cd
git clone https://github.com/sladecek/golem_cargo_test
```

4 Copy environment variables from the console running `goth` to the current shell. For example
```
export YAGNA_APPKEY=f9fe107ab0fb4de6a902d7ff38c1c7db
export YAGNA_API_URL=http://172.19.0.6:6000
export GSB_URL=tcp://172.19.0.6:6010
```

5 Add the script directory to the `PATH` environment variable.

# Custom image

If the project under test requires specific test data, or when the virtual machine configuration is not optimal, the user must prepare custom virtual machine using instructions at https://handbook.golem.network/requestor-tutorials/convert-a-docker-image-into-a-golem-image  and change the `image_hash` variable in the `golem_cargo_test` script.

# Running
1 Go to the directory containing the project to be tested.
```
cd ~\my-rust-project
```

2 Use the command:

```
golem_cargo_test
```

3 Add `--subnet=goth` argument when running in the *goth* test network.

4 Use `--plan` argument to define total run-time (default 300 seconds).

5 When run for the first time, no run-time statistic is available. It
is assumed, that each test runs for 60 seconds. This can be changed
using the `--test-avg` argument.

6 The total timeout is set to 30 minutes (can be changed by `--timeout`).

7 The executor builds the project to be tested and makes a list of tests.

8 The file `runtime.json` containing runtime statistics from the last
run is read. If no file exists, default value is used instead.

9 All tests are sorted by their duration (descending) and test binary
name. Then batches are formed. Each batch should contain as much tests
as possible as long as the total runtime is not exceeded. If a single
test is longer than the total runtime, it runs alone in a separate
batch.

10 All tasks are submitted to the *Golem*. The task first uploads the
test binary, then executes tests and finally downloads test results.

11 Finally, test results are combined and printed to the
console. Combined log is saved as `test_result.txt` file.


# Future Work

1 Support for other languages, such as *c++* or *javascript* should be added.
