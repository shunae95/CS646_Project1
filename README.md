<img src="UABCS.jpg" width=350>

# CS 646 Blockchain and Cryptocurrency - Fall 2022

# Group 2 - Project 4

##  How to run project
1.  Run the Node_XXXX.py file located in the each Miner Node folder.
    > The 4 digit number followed after the 'Node_' portion of the filename is the port that Node uses.
    > The new wallets connect to a new miner node randomly upon startup, but both nodes will receive transactions and blocks.
    > The wallet for the miner is also located in the folder as a Wallet.py file, and the wallet address is visible upon node startup.
    > All node files have require at least one transaction before beginnging constant mining begins.
    > The target that constitutes a successful mine and proof of work is in the proof function located in the Block.py file (packaged in every node folder).
    > Hashroot of tranasctions are calculated and output into hashroot.txt in the node folder.
2.  Run the Wallet.py file for the respective wallet you wish to use.
3.  Once executed, you will be greeted with a prompt with the following options:
    - Check local wallet balance - Will display the balance of the current wallet.
    - Check wallet balance using address - Will ask the user for an address and present the value associated with the respective wallet.
    - Create a transaction - Will create a valid transaction, asking for the recipient's address along with the amount to be sent. If the digital signature assigned to the transaction does not belong to the sender or the user does not have enough balance, it will not be created.
    - Exit application and process transactions - Closes the wallet interface.

  

## Authors
- [Tiara King](https://github.com/shunae95)
- [AJ Nettles](https://github.com/DelMonteAJ)
- [Leigh Allison](https://github.com/Ldallison)
  
<a href="https://github.com/shunae95/CS646_Project1/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ldallison/CS646_Project1" />
</a>

---
### Notes
> The initial transaction with the hash of "f91a588226a79b5d40f3bb0012bf2b51b10fa3b3ebb82346d3f070191d983ae8" is seen as the genesis transaction and creates the inital deposit of 100 coins into the system.
> Signatures.json in each node folder holds the transactions' hash and associated signature for future verification if desired.