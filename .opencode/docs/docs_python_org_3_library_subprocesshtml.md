# subprocess — Subprocess management &#8212; Python 3.14.7 documentation

> Source: https://docs.python.org/3/library/subprocess.html
> Cached: 2026-09-10T08:45:51.097Z

---

Theme
    
        Auto
        Light
        Dark
    

  
    ### [Table of Contents](../contents.html)

    

[`subprocess` — Subprocess management](#)

[Using the `subprocess` Module](#using-the-subprocess-module)

- [Frequently Used Arguments](#frequently-used-arguments)

- [Popen Constructor](#popen-constructor)

- [Exceptions](#exceptions)

- [Security Considerations](#security-considerations)

- [Popen Objects](#popen-objects)

[Windows Popen Helpers](#windows-popen-helpers)

- [Windows Constants](#windows-constants)

- [Older high-level API](#older-high-level-api)

[Replacing Older Functions with the `subprocess` Module](#replacing-older-functions-with-the-subprocess-module)

- [Replacing **/bin/sh** shell command substitution](#replacing-bin-sh-shell-command-substitution)

- [Replacing shell pipeline](#replacing-shell-pipeline)

- [Replacing `os.system()`](#replacing-os-system)

- [Replacing the `os.spawn` family](#replacing-the-os-spawn-family)

- [Replacing `os.popen()`](#replacing-os-popen)

- [Legacy Shell Invocation Functions](#legacy-shell-invocation-functions)

[Notes](#notes)

- [Timeout Behavior](#timeout-behavior)

- [Converting an argument sequence to a string on Windows](#converting-an-argument-sequence-to-a-string-on-windows)

- [Disable use of `posix_spawn()`](#disable-use-of-posix-spawn)

  
  
    #### Previous topic

    [`concurrent.interpreters` — Multiple interpreters in the same process](concurrent.interpreters.html)
  
  
    #### Next topic

    [`sched` — Event scheduler](sched.html)
  
  
  
    ### This page

    

      - [Report a bug](../bugs.html)

      - [Improve this page](../improve-page-nojs.html)

      
        Show source
        
      
      
    

  
        
    

  
    
      ### Navigation

      

        
          [index](../genindex.html)
        
          [modules](../py-modindex.html) |
        
          [next](sched.html) |
        
          [previous](concurrent.interpreters.html) |

          - 

          - [Python](https://www.python.org/) &#187;

          
            
            
          
          
              
          
    
      [3.14.7 Documentation](../index.html) &#187;
    

          - [The Python Standard Library](index.html) &#187;

          - [Concurrent Execution](concurrency.html) &#187;

        - [`subprocess` — Subprocess management]()

                
                    

    
        
          
          
        
    
                     |
                
            

    Theme
    
        Auto
        Light
        Dark
    
 |
            
      

        

    
      
        
          
            
  
# `subprocess` — Subprocess management[¶](#module-subprocess)

**Source code:** [Lib/subprocess.py](https://github.com/python/cpython/tree/3.14/Lib/subprocess.py)

The `subprocess` module allows you to spawn new processes, connect to their
input/output/error pipes, and obtain their return codes.  This module intends to
replace several older modules and functions:
os.system
os.spawn*

Information about how the `subprocess` module can be used to replace these
modules and functions can be found in the following sections.

See also

[**PEP 324**](https://peps.python.org/pep-0324/) – PEP proposing the subprocess module

[Availability](intro.html#availability): not Android, not iOS, not WASI.

This module is not supported on [mobile platforms](intro.html#mobile-availability)
or [WebAssembly platforms](intro.html#wasm-availability).

## Using the `subprocess` Module[¶](#using-the-subprocess-module)

The recommended approach to invoking subprocesses is to use the [`run()`](#subprocess.run)
function for all use cases it can handle. For more advanced use cases, the
underlying [`Popen`](#subprocess.Popen) interface can be used directly.

subprocess.run(*args*, ***, *stdin=None*, *input=None*, *stdout=None*, *stderr=None*, *capture_output=False*, *shell=False*, *cwd=None*, *timeout=None*, *check=False*, *encoding=None*, *errors=None*, *text=None*, *env=None*, *universal_newlines=None*, ***other_popen_kwargs*)[¶](#subprocess.run)
Run the command described by *args*.  Wait for command to complete, then
return a [`CompletedProcess`](#subprocess.CompletedProcess) instance.
The arguments shown above are merely the most common ones, described below
in [Frequently Used Arguments](#frequently-used-arguments) (hence the use of keyword-only notation
in the abbreviated signature). The full function signature is largely the
same as that of the [`Popen`](#subprocess.Popen) constructor - most of the arguments to
this function are passed through to that interface. (*timeout*,  *input*,
*check*, and *capture_output* are not.)
If *capture_output* is true, stdout and stderr will be captured.
When used, the internal [`Popen`](#subprocess.Popen) object is automatically created with
*stdout* and *stderr* both set to [`PIPE`](#subprocess.PIPE).
The *stdout* and *stderr* arguments may not be supplied at the same time as *capture_output*.
If you wish to capture and combine both streams into one,
set *stdout* to `PIPE`
and *stderr* to [`STDOUT`](#subprocess.STDOUT),
instead of using *capture_output*.
A *timeout* may be specified in seconds, it is internally passed on to
[`Popen.communicate()`](#subprocess.Popen.communicate). If the timeout expires, the child process will be
killed and waited for. The [`TimeoutExpired`](#subprocess.TimeoutExpired) exception will be
re-raised after the child process has terminated. The initial process
creation itself cannot be interrupted on many platform APIs so you are not
guaranteed to see a timeout exception until at least after however long
process creation takes.
The *input* argument is passed to [`Popen.communicate()`](#subprocess.Popen.communicate) and thus to the
subprocess’s stdin.  If used it must be a byte sequence, or a string if
*encoding* or *errors* is specified or *text* is true.  When
used, the internal [`Popen`](#subprocess.Popen) object is automatically created with
*stdin* set to [`PIPE`](#subprocess.PIPE),
and the *stdin* argument may not be used as well.
If *check* is true, and the process exits with a non-zero exit code, a
[`CalledProcessError`](#subprocess.CalledProcessError) exception will be raised. Attributes of that
exception hold the arguments, the exit code, and stdout and stderr if they
were captured.
If *encoding* or *errors* are specified, or *text* is true,
file objects for stdin, stdout and stderr are opened in text mode using the
specified *encoding* and *errors* or the [`io.TextIOWrapper`](io.html#io.TextIOWrapper) default.
The *universal_newlines* argument is equivalent  to *text* and is provided
for backwards compatibility. By default, file objects are opened in binary mode.
If *env* is not `None`, it must be a mapping that defines the environment
variables for the new process; these are used instead of the default
behavior of inheriting the current process’ environment. It is passed
directly to [`Popen`](#subprocess.Popen). This mapping can be str to str on any platform
or bytes to bytes on POSIX platforms much like [`os.environ`](os.html#os.environ) or
[`os.environb`](os.html#os.environb).
Examples:

>>> subprocess.run(["ls", "-l"])  # doesn't capture output
CompletedProcess(args=['ls', '-l'], returncode=0)

>>> subprocess.run("exit 1", shell=True, check=True)
Traceback (most recent call last):
  ...
subprocess.CalledProcessError: Command 'exit 1' returned non-zero exit status 1

>>> subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)
CompletedProcess(args=['ls', '-l', '/dev/null'], returncode=0,
stdout=b'crw-rw-rw- 1 root root 1, 3 Jan 23 16:23 /dev/null\n', stderr=b'')

Added in version 3.5.

Changed in version 3.6: Added *encoding* and *errors* parameters

Changed in version 3.7: Added the *text* parameter, as a more understandable alias of *universal_newlines*.
Added the *capture_output* parameter.

Changed in version 3.12: Changed Windows shell search order for `shell=True`. The current
directory and `%PATH%` are replaced with `%COMSPEC%` and
`%SystemRoot%\System32\cmd.exe`. As a result, dropping a
malicious program named `cmd.exe` into a current directory no
longer works.

*class *subprocess.CompletedProcess[¶](#subprocess.CompletedProcess)
The return value from [`run()`](#subprocess.run), representing a process that has finished.

args[¶](#subprocess.CompletedProcess.args)
The arguments used to launch the process. This may be a list or a string.

returncode[¶](#subprocess.CompletedProcess.returncode)
Exit status of the child process. Typically, an exit status of 0 indicates
that it ran successfully.
A negative value `-N` indicates that the child was terminated by signal
`N` (POSIX only).

stdout[¶](#subprocess.CompletedProcess.stdout)
Captured stdout from the child process. A bytes sequence, or a string if
[`run()`](#subprocess.run) was called with an encoding, errors, or text=True.
`None` if stdout was not captured.
If you ran the process with `stderr=subprocess.STDOUT`, stdout and
stderr will be combined in this attribute, and [`stderr`](#subprocess.CompletedProcess.stderr) will be
`None`.

stderr[¶](#subprocess.CompletedProcess.stderr)
Captured stderr from the child process. A bytes sequence, or a string if
[`run()`](#subprocess.run) was called with an encoding, errors, or text=True.
`None` if stderr was not captured.

check_returncode()[¶](#subprocess.CompletedProcess.check_returncode)
If [`returncode`](#subprocess.CompletedProcess.returncode) is non-zero, raise a [`CalledProcessError`](#subprocess.CalledProcessError).

Added in version 3.5.

subprocess.DEVNULL[¶](#subprocess.DEVNULL)
Special value that can be used as the *stdin*, *stdout* or *stderr* argument
to [`Popen`](#subprocess.Popen) and indicates that the special file [`os.devnull`](os.html#os.devnull)
will be used.

Added in version 3.3.

subprocess.PIPE[¶](#subprocess.PIPE)
Special value that can be used as the *stdin*, *stdout* or *stderr* argument
to [`Popen`](#subprocess.Popen) and indicates that a pipe to the standard stream should be
opened.  Most useful with [`Popen.communicate()`](#subprocess.Popen.communicate).

subprocess.STDOUT[¶](#subprocess.STDOUT)
Special value that can be used as the *stderr* argument to [`Popen`](#subprocess.Popen) and
indicates that standard error should go into the same handle as standard
output.

*exception *subprocess.SubprocessError[¶](#subprocess.SubprocessError)
Base class for all other exceptions from this module.

Added in version 3.3.

*exception *subprocess.TimeoutExpired[¶](#subprocess.TimeoutExpired)
Subclass of [`SubprocessError`](#subprocess.SubprocessError), raised when a timeout expires
while waiting for a child process.

cmd[¶](#subprocess.TimeoutExpired.cmd)
Command that was used to spawn the child process.

timeout[¶](#subprocess.TimeoutExpired.timeout)
Timeout in seconds.

output[¶](#subprocess.TimeoutExpired.output)
Output of the child process if it was captured by [`run()`](#subprocess.run) or
[`check_output()`](#subprocess.check_output).  Otherwise, `None`.  This is always
[`bytes`](stdtypes.html#bytes) when any output was captured regardless of the
`text=True` setting.  It may remain `None` instead of `b''`
when no output was observed.

stdout[¶](#subprocess.TimeoutExpired.stdout)
Alias for output, for symmetry with [`stderr`](#subprocess.TimeoutExpired.stderr).

stderr[¶](#subprocess.TimeoutExpired.stderr)
Stderr output of the child process if it was captured by [`run()`](#subprocess.run).
Otherwise, `None`.  This is always [`bytes`](stdtypes.html#bytes) when stderr output
was captured regardless of the `text=True` setting.  It may remain
`None` instead of `b''` when no stderr output was observed.

Added in version 3.3.

Changed in version 3.5: *stdout* and *stderr* attributes added

*exception *subprocess.CalledProcessError[¶](#subprocess.CalledProcessError)
Subclass of [`SubprocessError`](#subprocess.SubprocessError), raised when a process run by
[`check_call()`](#subprocess.check_call), [`check_output()`](#subprocess.check_output), or [`run()`](#subprocess.run) (with `check=True`)
returns a non-zero exit status.

returncode[¶](#subprocess.CalledProcessError.returncode)
Exit status of the child process, an integer.  If the process
exited due to a signal, this will be the negative signal number.

cmd[¶](#subprocess.CalledProcessError.cmd)
Command that was used to spawn the child process.

output[¶](#subprocess.CalledProcessError.output)
Output of the child process if it was captured by [`run()`](#subprocess.run) or
[`check_output()`](#subprocess.check_output).  Otherwise, `None`.

stdout[¶](#subprocess.CalledProcessError.stdout)
Alias for output, for symmetry with [`stderr`](#subprocess.CalledProcessError.stderr).

stderr[¶](#subprocess.CalledProcessError.stderr)
Stderr output of the child process if it was captured by [`run()`](#subprocess.run).
Otherwise, `None`.

Changed in version 3.5: *stdout* and *stderr* attributes added

### Frequently Used Arguments[¶](#frequently-used-arguments)

To support a wide variety of use cases, the [`Popen`](#subprocess.Popen) constructor (and
the convenience functions) accept a large number of optional arguments. For
most typical use cases, many of these arguments can be safely left at their
default values. The arguments that are most commonly needed are:
> 
*args* is required for all calls and should be a string, or a sequence of
program arguments. Providing a sequence of arguments is generally
preferred, as it allows the module to take care of any required escaping
and quoting of arguments (e.g. to permit spaces in file names). If passing
a single string, either *shell* must be [`True`](constants.html#True) (see below) or else
the string must simply name the program to be executed without specifying
any arguments.
*stdin*, *stdout* and *stderr* specify the executed program’s standard input,
standard output and standard error file handles, respectively.  Valid values
are `None`, [`PIPE`](#subprocess.PIPE), [`DEVNULL`](#subprocess.DEVNULL), an existing file descriptor (a
positive integer), and an existing [file object](../glossary.html#term-file-object) with a valid file
descriptor.  With the default settings of `None`, no redirection will
occur.  `PIPE` indicates that a new pipe to the child should be
created.  `DEVNULL` indicates that the special file [`os.devnull`](os.html#os.devnull)
will be used.  Additionally, *stderr* can be [`STDOUT`](#subprocess.STDOUT), which indicates
that the stderr data from the child process should be captured into the same
file handle as for *stdout*.
If *encoding* or *errors* are specified, or *text* (also known as
*universal_newlines*) is true,
the file objects *stdin*, *stdout* and *stderr* will be opened in text
mode using the *encoding* and *errors* specified in the call or the
defaults for [`io.TextIOWrapper`](io.html#io.TextIOWrapper).
For *stdin*, line ending characters `'\n'` in the input will be converted
to the default line separator [`os.linesep`](os

... [Content truncated]