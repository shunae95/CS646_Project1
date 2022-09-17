# CS646_Project1

##  How to run project
1.  Run the Main.py, executing this file will prompt the user for the needed information to generate a transaction.
2.  After creating your transaction it will be placed in a "pending" folder that until all transactions are created.
3.  When the user inputs that all transactions have been created, a block will be created and each transaction will be moved from the "pending" folder to a "processed" folder after being added to the block. 
4.  To create an additional block, the user must executed the Main.py script again. Each block is created and labeled as a JSON file with the prefix "B_" followed by the block's height. The starting block will be displayed as "B_0.json".