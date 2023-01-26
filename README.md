# Unix_base_File_System_Project
This is an Unix distributed file system program
In this project, I designed a multi-client/multi-servers UNIX-based file system which supports data distribution to multiple servers, 
RAID5 storage mode is implemented so that client side can communicate with multiple servers by RPC, 
and servers can execute requests in parallel, that will improve the system throughput. 
Meanwhile, this file system has the ability for tolerating fault by using the parity, when one server failed or block 
corrupted, it can continue to work and has ability to repair to normal. 
