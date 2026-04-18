# Short Reflections

## Why did you choose your base image?
I picked the maze because it didn't require a `.venv` or imports of `pygame`. If a random machine runs the text-based maze, it only needs the terminal.

## What was the trickiest part of getting the Dockerfile right? What path or configuration issues did you encounter?
Step 4: Connect via SSH. I thought I had to do this on a Linux VM, so I used the VM I set up for Robert's class, 505. It was extremely time consuming and difficult. Then I reread your instructions and realized I could do these steps in VS Code or Cursor.

## How does `WORKDIR` in your Dockerfile relate to how you normally run the maze?
`WORKDIR` is like my `maze_quiz` folder that I save my maze quiz files in locally, or the folder I would open on my desktop. The `WORKDIR` is the Docker version of that.

## What is the difference between a Docker image and a container?
An image is the saved template, while a container is the running version of that template.

## What did you learn from the Docker Hub push/pull cycle? Why are registries useful?
Docker push/pull works very much like GitHub. The registry is useful because everyone pulls the same image.

## What did AI get wrong or suggest incorrectly when helping with the Dockerfile, and how did you fix it?
AI had a lot of problems with connecting to EC2. It wanted me checking the subnet ID, among other dead ends, on AWS. I kept steering it back because the instance was showing 2/3 tests passed, and after several other things, it finally had me restart the instance, which worked. I think my instance failed a test because of a timeout. I'm still not exactly sure.