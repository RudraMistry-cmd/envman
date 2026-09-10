# Redis CLI | Docs

> Source: https://redis.io/docs/latest/develop/tools/cli/
> Cached: 2026-09-10T08:47:51.160Z

---

Develop with Redis
        
          

            
      
        
          
          Get started
      
      
    
      
        
          
          What's new?
      
      
    
      
        
          
          Quick starts
      
      
    
      
        
          
          Client tools
      
      
    
      

        
      
        CLI
      
      
    
      
        
          
          Redis Insight
      
      
    
      
        
          
          Redis for VS Code
      
      
    
      

    
      
        
          
          Client APIs
      
      
    
      
        
          
          Using commands
      
      
    
      
        
          
          Data types
      
      
    
      
        
          
          Redis for AI and search
      
      
    
      
        
          
          Programmability
      
      
    
      
        
          
          Use cases
      
      
    
      
        
          
          Pub/sub
      
      
    
      
        
          
          Reference
      
      
    
          

        
        Libraries and tools
        
        Redis products
        
      
      
        Commands
        
      
    
      

  
    Download documentation
    
      
      
      
    
  

    
    

  
    
      
        
          Download documentation
        
        
          Choose the products and versions you want. Everything arrives as one
          `.tar.gz`, with a directory per product.
        
      
      
        
          
        
      
    

    

      
        Format
        
          
            
              Markdown &mdash; one .md file per page
            
          
            
              Markdown, single file &mdash; every page in one .md file
            
          
            
              HTML &mdash; browse offline
            
          
            
              JSON &mdash; one .json file per page
            
          
        
      
      

      
      
        
          
            
              This page
              
            
          
          
            
              
                
                
              
              
                
                  Download
                
              
            
          
        
      

      
        
          
            
              
                
              
              Products
              Version
            
          
          
            
              
                
                  
                
                
                  
                    Develop with Redis
                  
                  
                    Clients, data types, programmability, and Redis for AI. RedisVL is listed separately.
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Libraries and tools
                  
                  
                    Client libraries, observability, and cloud integrations. Redis Data Integration is listed separately.
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    RedisVL
                  
                  
                
                
                  
                    
                      latest
                      
                        v0.27.0
                      
                        v0.26.0
                      
                        v0.25.1
                      
                        v0.25.0
                      
                        v0.24.0
                      
                        v0.23.0
                      
                        v0.22.0
                      
                        v0.20.1
                      
                        v0.20.0
                      
                        v0.19.0
                      
                        v0.18.2
                      
                        v0.18.1
                      
                        v0.18.0
                      
                        v0.17.1
                      
                        v0.17.0
                      
                        v0.16.0
                      
                        v0.15.0
                      
                        v0.14.0
                      
                        v0.13.2
                      
                        v0.13.0
                      
                        v0.12.1
                      
                        v0.12.0
                      
                        v0.11.1
                      
                        v0.11.0
                      
                        v0.10.0
                      
                        v0.9.1
                      
                        v0.9.0
                      
                        v0.8.2
                      
                        v0.8.1
                      
                        v0.8.0
                      
                        v0.7.0
                      
                        v0.6.0
                      
                    
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Software
                  
                  
                
                
                  
                    
                      latest
                      
                        v8.0
                      
                        v7.22
                      
                        v7.8
                      
                        v7.4
                      
                    
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Cloud
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Redis for Kubernetes
                  
                  
                
                
                  
                    
                      latest
                      
                        v8.0.18
                      
                        v8.0
                      
                        v7.22
                      
                        v7.8.6
                      
                        v7.8.4
                      
                        v7.4.6
                      
                    
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Open Source
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Iris context engine
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Feature Form
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Insight
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Redis Data Integration
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Glossary
                  
                  
                
                
                  
                
              
            
              
                
                  
                
                
                  
                    Command reference
                  
                  
                
                
                  
                
              
            
          
        
      

      
        

        
          Cancel
        
        
          Download
        
      
    
  

  

    
      
 
  

    
  
    
  
    
  
    
  
  
    
      
        
        
        Docs
        Docs
      
    
  

  
  
    
      →
      
        Develop with Redis
      
    
  

  
  
    
      →
      
        Client tools
      
    
  

  
  
    
      →
      
        Redis CLI
      
    
  

  

      
        
          Redis CLI
        Overview of redis-cli, the Redis command line interface

        
        
        
          
          
          
            
          
          
          
            
            
          
            
            
          
            
            
          
        
        
        In interactive mode, `redis-cli` has basic line editing capabilities to provide a familiar typing experience.

To launch the program in special modes, you can use several options, including:

- Simulate a replica and print the replication stream it receives from the primary.

- Check the latency of a Redis server and display statistics.

- Request ASCII-art spectrogram of latency samples and frequencies.

This topic covers the different aspects of `redis-cli`, starting from the simplest and ending with the more advanced features.

  Install `redis-cli`
  
    
      
    
  

You have several options for installing or using `redis-cli`. The easiest method is to install the standalone `redis-cli` binary for Linux or macOS. See the [Install redis-cli](/docs/latest/operate/oss_and_stack/install/install-stack/install-redis-cli/) page for more information.

Other methods include:

[Install Redis Open Source](/docs/latest/operate/oss_and_stack/install/install-stack/). The `redis-cli` utility is installed as part of each installation method.

[Build Redis from source](/docs/latest/operate/oss_and_stack/install/build-stack/). Instead of building everything, you can just run the following command:

`$ make redis-cli`.

The `redis-cli` utility will be built in the `/path/to/redis-source/src` directory as `/path/to/redis-source/src/redis-cli`.

If you prefer not to install Redis, you can also run `redis-cli` in Docker. See the [Run `redis-cli` using Docker](/docs/latest/operate/oss_and_stack/install/install-stack/docker/#connect-with-redis-cli) page for instructions.

  Command line usage
  
    
      
    
  

To run a Redis command and return a standard output at the terminal, include the command to execute as separate arguments of `redis-cli`:

```
$ redis-cli INCR mycounter
(integer) 7

```

The reply of the command is "7". Since Redis replies are typed (strings, arrays, integers, nil, errors, etc.), you see the type of the reply between parentheses. This additional information may not be ideal when the output of `redis-cli` must be used as input of another command or redirected into a file.

`redis-cli` only shows additional information for human readability when it detects the standard output is a tty, or terminal. For all other outputs it will auto-enable the *raw output mode*, as in the following example:

```
$ redis-cli INCR mycounter > /tmp/output.txt
$ cat /tmp/output.txt
8

```

Note that `(integer)` is omitted from the output because `redis-cli` detects
the output is no longer written to the terminal. You can force raw output
even on the terminal with the `--raw` option:
```
$ redis-cli --raw INCR mycounter
9

```

You can force human readable output when writing to a file or in
pipe to other commands by using `--no-raw`.
For complete command line usage, see [below](#usage).

  String quoting and escaping
  
    
      
    
  

When `redis-cli` parses a command, whitespace characters automatically delimit the arguments.
In interactive mode, a newline sends the command for parsing and execution.
To input string values that contain whitespaces or non-printable characters, you can use quoted and escaped strings.
Quoted string values are enclosed in double (`"`) or single (`'`) quotation marks.
Escape sequences are used to put nonprintable characters in character and string literals.
An escape sequence contains a backslash (`\`) symbol followed by one of the escape sequence characters.

Doubly-quoted strings support the following escape sequences:

- `\"` - double-quote

- `\n` - newline

- `\r` - carriage return

- `\t` - horizontal tab

- `\b` - backspace

- `\a` - alert

- `\\` - backslash

- `\xhh` - any ASCII character represented by a hexadecimal number (*hh*)

Single quotes assume the string is literal, and allow only the following escape sequences:

- `\'` - single quote

- `\\` - backslash

For example, to return `Hello World` on two lines:

```
127.0.0.1:6379> SET mykey &#34;Hello\nWorld&#34;
OK
127.0.0.1:6379> GET mykey
Hello
World

```

When you input strings that contain single or double quotes, as you might in passwords, for example, escape the string, like so:

```
127.0.0.1:6379> AUTH some_admin_user &#34;>^8T>6Na{u|jp>+v\&#34;55\@_;OU(OR]7mbAYGqsfyu48(j'%hQH7;v*f1H${*gD(Se'&#34;

```

  Host, port, password, and database
  
    
      
    
  

By default, `redis-cli` connects to the server at the address 127.0.0.1 with port 6379.
You can change the port using several command line options. To specify a different host name or an IP address, use the `-h` option. In order to set a different port, use `-p`.
```
$ redis-cli -h redis15.localnet.org -p 6390 PING
PONG

```

If your instance is password protected, the `-a <password>` option will
perform authentication saving the need of explicitly using the [`AUTH`](/docs/latest/commands/auth/) command:
```
$ redis-cli -a myUnguessablePazzzzzword123 PING
PONG

```

**NOTE:** For security reasons, provide the password to `redis-cli` automatically via the
`REDISCLI_AUTH` environment variable.
Finally, it's possible to send a command that operates on a database number
other than the default number zero by using the `-n

... [Content truncated]