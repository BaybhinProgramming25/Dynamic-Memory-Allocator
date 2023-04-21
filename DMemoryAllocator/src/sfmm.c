/**
 * Do not submit your assignment with a main function in this file.
 * If you submit with a main function in this file, you will get a zero.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "debug.h"
#include "sfmm.h"


//THE ACTUAL METHODS STARTS AT LINE 

size_t makeMultipleOfAlignmentSize(size_t requestedSize) { //The purpose is to make this size a multiple of 32 in the event the size is greater

    //Minimum block size = 32, so anything lower than or equal to 24 will set to 32 automatically
    //ELse if we have a value greater than 32 and is not a multiple of 8, then we need to realign

    if(requestedSize <= 24) {
        return 32;
    }
    else if(requestedSize % 8 == 0) {
        return requestedSize + 8; //8 also for the header
    }
    else {

        int actualSize = requestedSize + 8; //8 also for the header
        int quotientModified = (actualSize / 8) + 1;
        return (quotientModified * 8);
    }

}


sf_block *checkQuickListAtSpecificIndex(size_t asize, int indexOfQuickList) {

    //Check the quick list at this index to see if there is a free block
    //So is the goal here to get the address of where to put the block? 

    if (sf_quick_lists[indexOfQuickList].length <= 0) return NULL;
    else if (sf_quick_lists[indexOfQuickList].length > 0) {

        //Since all the blocks here will be of the same size, we can take the first block
        //Delete from linked list, via deleting from the head so that it is O(1), because LIFO strategy

        sf_block *referenceToFirstBlock = sf_quick_lists[indexOfQuickList].first; //Get the first block in the list
        referenceToFirstBlock->header &= ~IN_QUICK_LIST; //Sets the bit to be off, indicating it is no longer in the quick list, because it is now allocated
        referenceToFirstBlock->header &= ~THIS_BLOCK_ALLOCATED; //We maybe do this?
        sf_quick_lists[indexOfQuickList].first = sf_quick_lists[indexOfQuickList].first->body.links.next;
        sf_quick_lists[indexOfQuickList].length -= 1; //Decrease the length
        return referenceToFirstBlock;
        
    }
    return NULL; //In the event this is somehow reached here, we also want to return NULL here
}

int coalesceFunction(sf_block *currentBlock);

int insertIntoQuickList(sf_block *blockToInsert, int indexOfQuickList) {


    //Before insertion, we need to check if the quick list is at its capacity
    //if the quick list is at its capacity, then we need to flush
    //and coalesce, if possible

    //Then, we need to coalesce -> add to main list -> then flush
    if(sf_quick_lists[indexOfQuickList].length == QUICK_LIST_MAX) {

        sf_block *quickListBLock = sf_quick_lists[indexOfQuickList].first;

        while(sf_quick_lists[indexOfQuickList].length != 0) {

            //Set the IN_QUICK_LIST bit to 0, and by default set the allocation bit to 0
            quickListBLock->header &= ~IN_QUICK_LIST; //Since we are flushing, set to 0
            quickListBLock->header &= ~THIS_BLOCK_ALLOCATED; //Also because we are fushing, set to 0
            sf_block *tempBlock = quickListBLock;
            coalesceFunction(tempBlock); //Send in a temp variable 
            quickListBLock = quickListBLock->body.links.next; //Go to the next node in the list 
            sf_quick_lists[indexOfQuickList].length -= 1; //Decrease the length 

        }

        //After we flushed out everything, coalesced, and added to the main list, we then add the node we want to add into the quick list

        sf_quick_lists[indexOfQuickList].first = blockToInsert;
        sf_quick_lists[indexOfQuickList].first->body.links.next = NULL; //Since only node in the list
        sf_quick_lists[indexOfQuickList].length += 1;
        blockToInsert->header |= IN_QUICK_LIST; //Set to 1
        blockToInsert->header |= THIS_BLOCK_ALLOCATED; //Set to 1
    }
    
    else { //Simple linked list insertion, where we insert from the head

        blockToInsert->body.links.next = sf_quick_lists[indexOfQuickList].first;
        sf_quick_lists[indexOfQuickList].first = blockToInsert;
        blockToInsert->header |= IN_QUICK_LIST; //Set to true
        blockToInsert->header |= THIS_BLOCK_ALLOCATED; //Set to true
        sf_quick_lists[indexOfQuickList].length += 1;

    }

    return 1;
}

int findIndexFromMainFreeLists(size_t sizeOfBlock);
int placeFreeBlockOfSizeX(sf_block *currentBlock, int indexToInsert);
int deleteBlockFromMainList(sf_block *currentBlock, int findIndex);

int coalesceFunction(sf_block *currentBlock) {

    sf_block *accessHeader = (sf_block*)((char*)currentBlock); //Get header of the current block

    size_t sizeOfCurrentBlock = (accessHeader->header & ~0x7); //Get size of the current block 

    int prevAllocBitStatus = (accessHeader->header & PREV_BLOCK_ALLOCATED); //1 means it (the previous block) is allocated, but the prologue is also allocated

    sf_block *nextBlock = (sf_block*)((char *)accessHeader + sizeOfCurrentBlock); //Takes us to header of next block

    size_t sizeOfNextBlock = (nextBlock->header & ~0x7); //Get size of the next block 

    int nextAllocBitStatus = (nextBlock->header & THIS_BLOCK_ALLOCATED);  //1 means it is allocated, but the epilogue is also allocated
    

    if(prevAllocBitStatus == 2 && nextAllocBitStatus == 1) { //Both blocks are allocated, so no coalescing

        //Set the allocation bit to 0 
        accessHeader->header &= ~THIS_BLOCK_ALLOCATED; //Since this block is now free
        accessHeader->header |= PREV_BLOCK_ALLOCATED; //Guaranteed for the previous block to be allocated, so make sure this is on

        //Set the footer to be equal to the header
        sf_footer *currentBlockFooter = (sf_footer*)((char*)accessHeader + sizeOfCurrentBlock - 8);
        *(currentBlockFooter) = accessHeader->header;

        //We also need to upate the header, and thus also make a footer

        //Also want to set the nextBlock's previous alloc bit to 0 to indicate not allocated
        nextBlock->header &= ~PREV_BLOCK_ALLOCATED; //Turn's this bit off 
        nextBlock->header |= THIS_BLOCK_ALLOCATED; //Guaranteed Allocated 

        int indexToInsertIntoMainList = findIndexFromMainFreeLists(sizeOfCurrentBlock);
        placeFreeBlockOfSizeX(currentBlock, indexToInsertIntoMainList);

    }
    else if (prevAllocBitStatus == 0 && nextAllocBitStatus == 1) {

        sf_footer *grabFooterPrev = (sf_footer*)((char*)accessHeader - 8); 
        //Access the footer of the prev block 
        size_t blockSize = (*grabFooterPrev & ~0x7); //Dereference to get the value and bit mask to get the block size

        int getPreviousBlockStatus = (*grabFooterPrev & PREV_BLOCK_ALLOCATED);

        size_t newCoalescedSize = blockSize + sizeOfCurrentBlock;

        //Access the header from the footer 

        sf_block *getHeader = (sf_block*)((char*)accessHeader - blockSize);

        getHeader->header = newCoalescedSize | getPreviousBlockStatus; //Header gets updated, and preserve the previousblock status
        getHeader->header &= ~THIS_BLOCK_ALLOCATED; //Set to 0

        //We are need to update the footer
        size_t newHeaderBlockSize = (getHeader->header & ~0x7);

        sf_footer *getFooterNew = (sf_footer*)((char*)getHeader + newHeaderBlockSize - 8);
        *(getFooterNew) = getHeader->header; //Footer has been updated 

        //Update the bits for the next block
        //Set the previous alloc bit to 0 since free memory
        //Keep the currently allocated bit to 1 
        nextBlock->header &= ~PREV_BLOCK_ALLOCATED; //Set to 0
        nextBlock->header |= THIS_BLOCK_ALLOCATED; //This block is clearly allocated
        
        //Once we have coalesced, we now then need to remove the original node from the main free list

        int findIndex = findIndexFromMainFreeLists(blockSize); //Remove original block size
        deleteBlockFromMainList(getHeader, findIndex);

        int findIndexToInsert = findIndexFromMainFreeLists(newCoalescedSize);
        placeFreeBlockOfSizeX(getHeader, findIndexToInsert);

    }
    else if (prevAllocBitStatus == 2 && nextAllocBitStatus == 0) {

        //This means that the next block is a free memory
        //But the previous block isn't 

        //We need to set this block to be free

        int statusOfPrevious = (accessHeader->header & PREV_BLOCK_ALLOCATED);

        size_t newCoalescedSize = sizeOfCurrentBlock + sizeOfNextBlock; 

        //The previous block is still allocated, so we need to do this 

        accessHeader->header = newCoalescedSize | statusOfPrevious;
        accessHeader->header &= ~THIS_BLOCK_ALLOCATED; //Set's the THIS_BLOCK_ALLOCATED TO 0, indicating its free

        //Set the prev_alloc bit of the combined header to be 1 while preserving its value

        size_t grabNewSize = (accessHeader->header & ~0x7);

        //Set up the footer
        sf_footer *goToFooter = (sf_footer*)((char*)accessHeader + grabNewSize - 8);
        *(goToFooter) = accessHeader->header;

        sf_block *goFurtherInHeap = (sf_block*)((char*)nextBlock + sizeOfNextBlock);

        int statusOfBlock = (goFurtherInHeap->header & THIS_BLOCK_ALLOCATED);

        goFurtherInHeap->header &= ~PREV_BLOCK_ALLOCATED; //Sets prev_alloc to 0 
        goFurtherInHeap->header |= statusOfBlock; //Preserve block status

        //Delete the free block that was next to the original currentblock
        int findIndex = findIndexFromMainFreeLists(sizeOfNextBlock);
        deleteBlockFromMainList(nextBlock, findIndex);

        int findIndexToInsert = findIndexFromMainFreeLists(newCoalescedSize);
        placeFreeBlockOfSizeX(currentBlock, findIndexToInsert);
        
    }
    else if (prevAllocBitStatus == 0 && nextAllocBitStatus == 0) { //Both blocks are free

        //Both blocks are free, so major coalescing will be happening here
        //We need to grab the previous block and the next block

        sf_footer *grabFooterPrev = (sf_footer*)((char*)accessHeader - 8); 
        //Access the footer of the prev block 
        size_t blockSizePrevius = (*grabFooterPrev & ~0x7);

        //*grabFooterPrev == header size
        //*grabFooterPrev & ~0x7 == block size
        int getMorePreviousBlockStatus = (*grabFooterPrev & PREV_BLOCK_ALLOCATED); //This needs to be preserved

        //Grab the next block, which we already have

        size_t entireCoalesce = blockSizePrevius + sizeOfCurrentBlock + sizeOfNextBlock; //Our total coalesced block
        

        //Before updating the header, lets go to the block after the next block and update
        //the bits for those

        sf_block *getFurtherBlock = (sf_block *)((char*)nextBlock + sizeOfNextBlock);

        //WE don't know if this block is free or allocated
        int furtherBlockStatus = (getFurtherBlock->header & THIS_BLOCK_ALLOCATED);
        getFurtherBlock->header &= ~PREV_BLOCK_ALLOCATED; //Set previous block to be allocated
        getFurtherBlock->header |= furtherBlockStatus;

        //Go to the header of where the merging is going to take place

        sf_block *accessMergingHeader = (sf_block*)(accessHeader - blockSizePrevius);
        accessMergingHeader->header = entireCoalesce | getMorePreviousBlockStatus; //Preserve the previous_alloc bit
        accessMergingHeader->header &= ~THIS_BLOCK_ALLOCATED; //Set this to 0 since it is a free block 

        //Now we need to delete both the original next block and the original previous block from the main free list

        int findIndexPrevious = findIndexFromMainFreeLists(blockSizePrevius);
        deleteBlockFromMainList(accessMergingHeader, findIndexPrevious);
        
        int findIndexNext = findIndexFromMainFreeLists(sizeOfNextBlock);
        deleteBlockFromMainList(nextBlock, findIndexNext);

        //Now merge
        int findIndexToInsert = findIndexFromMainFreeLists(entireCoalesce);
        placeFreeBlockOfSizeX(accessMergingHeader, findIndexToInsert);

    }

    return 1; //To indicate we are done coalescing, and inserting into the free list 
}


int findIndexFromMainFreeLists(size_t asize) {

    size_t lowerBound = 32; //M
    size_t upperBound = 64; //2M
    size_t indexFound = -1; //Since our index could potentially be 0

    for(int i = 0; i < NUM_FREE_LISTS; i++) { //First find the index that will satisfy the request

        if(i == 0) {
            if(asize == lowerBound) {
                indexFound = i;
                return indexFound;
            }
        }
        else if (i != NUM_FREE_LISTS - 1) {
            if((lowerBound < asize) && (asize <= upperBound)) {
                indexFound = i;
                return indexFound;
            }  
            int divisor = upperBound / lowerBound;
            lowerBound = upperBound;
            upperBound = (upperBound * divisor);
        }
        else { //When looking at the last index before the total number of lists
            if(asize > upperBound) {
                indexFound = i;
                return indexFound;
            }
        }
    }

    return NUM_FREE_LISTS - 1; //In the event that we still can't find index, so we just set to the last free list 
}

int placeFreeBlockOfSizeX(sf_block *freeBlock, int main_free_list_location) { //Inserting into the linked list

    //LAST-IN-FIRST-OUT mechanism, in which we are going to be inserting nodes right
    //in front of the sentinel node 

    sf_block *sentinelNode = &sf_free_list_heads[main_free_list_location];
    sf_block *nextBlock = sentinelNode->body.links.next;
    sentinelNode->body.links.next = freeBlock;
    nextBlock->body.links.prev = freeBlock;
    freeBlock->body.links.next = nextBlock;
    freeBlock->body.links.prev = sentinelNode;

    return 1; //To indicate success
}

int deleteBlockFromMainList(sf_block *blockToDelete, int main_free_list_location) {

    //Once found, we need to get a reference to the previous block and a reference to the next block
    sf_block *previousBlock = blockToDelete->body.links.prev;
    sf_block *nextBlock = blockToDelete->body.links.next;
    previousBlock->body.links.next = nextBlock;
    nextBlock->body.links.prev = previousBlock;

    return 1; //To indicate success


}

int checkMemStartMemEnd() {

    if((char*)sf_mem_end() - (char*)sf_mem_start() == 0) { //Tells us that the heap beginning and heap ending are the same, so we need to allocate more space by a magnitude of 1 page
        //Edge case where the heap is essentially pointing at the same place

        char *growHeap = sf_mem_grow();  //Will return us the address of where the heap actually begins
        //This is also going to be the first initialization, but just to be sure, set ENOMEM

        if(growHeap == NULL) {
            sf_errno = ENOMEM;
            return 0;
        }

        sf_block *prologueBlock = (sf_block *)(growHeap); 
        //Now we need to set the allocation bit of the prologue to 0, indicating
        prologueBlock->header = 0x00000020 | THIS_BLOCK_ALLOCATED; //Set the header to the allocated bit, and 0x20 (32) represents the size of the block since this is the minimum size that we eneed

        //Now we also need to set the epilogue, which only contains a header 

        sf_block *epilogueBlock = (sf_block*)((char *)sf_mem_end() - 8); //sh_mem_end() points to a byte following end of the heap, so subtract 8 bytes to get where the epilogue is
        epilogueBlock->header = 0x00000000 | THIS_BLOCK_ALLOCATED; //Epologue block has size of 0, but we set the allocated bit to 1

        //Initialize the quick lists

        for (int i = 0; i < NUM_QUICK_LISTS; i++) {

            sf_quick_lists[i].first = NULL; 
            sf_quick_lists[i].length = 0; //Set the length to 0
        }

        //Next, we need to initialize the circular doubly linked list (aka the main free list)

        for(int i = 0; i < NUM_FREE_LISTS; i++) {

            sf_free_list_heads[i].body.links.next = &sf_free_list_heads[i];
            sf_free_list_heads[i].body.links.prev = &sf_free_list_heads[i];

            //This is the process of setting back to itself
        }

        //After initializing, we need to consider the firstMemBlockSize
        // The first size is going to be 4096 (page size) - 32 (prologue size) - 8 (epilogue size) = 4056 bytes (free block size for header, payload, and padding)

        size_t initialFirstBlockSize = (PAGE_SZ - 40);

        sf_block *initalFirstBlock = (sf_block*)((char *)prologueBlock + 32); //Since 32 is the size of prologue, which we allocated
        initalFirstBlock->header = initialFirstBlockSize | PREV_BLOCK_ALLOCATED; //Since the prev block we allocated is the prologue, so we set to true

        size_t blockSize = (initalFirstBlock->header & ~0x7);

        sf_footer *footer = (sf_footer*)((char *)initalFirstBlock + blockSize - 8); // Cast address to  char
        *(footer) = initalFirstBlock->header; //Setting the footer to be the header 

        //Now we need to put the first free block in the main free list 
        //WE can simply run the algorithm to find where to put the first free block
        int findIndexToPutFirstFreeBlock = findIndexFromMainFreeLists(initialFirstBlockSize);
        placeFreeBlockOfSizeX(initalFirstBlock, findIndexToPutFirstFreeBlock);

    }
    return 1;
}

int checkForSplinter(sf_block *blockFound, size_t adjustedSize) {

    //We first get the block size

    size_t blockSize = (blockFound->header & ~0x7); //The address is currently at the header 
    size_t differenceSizeNeeded = blockSize - adjustedSize;

    if(differenceSizeNeeded < 32) return 1; //SPlinter found
    return 0; //No splinter found 
}

void *computeSplinter(int splinterValue, sf_block *blockToInvestigate, size_t aSize) {

    void *mallocReturnAddr = NULL;

    if(splinterValue == 1) { //Splinter may occur, so take the whole value 

        mallocReturnAddr = (char *)((char *)blockToInvestigate + 8); //We need to send payload, not the header

        blockToInvestigate->header |= THIS_BLOCK_ALLOCATED; //Set allocation status

        size_t blockSize = (blockToInvestigate->header & ~0x7);

        //Must let any other blocks in the future know that this is allocated

        sf_block *futureBlock = (sf_block*)((char*)blockToInvestigate + blockSize);
        futureBlock->header |= PREV_BLOCK_ALLOCATED;

        //Remove from the free list 

        int findIndex = findIndexFromMainFreeLists(blockSize);
        deleteBlockFromMainList(blockToInvestigate, findIndex);

    }
    else if(splinterValue == 0) { //It is safe to split

        size_t blockSize = (blockToInvestigate->header & ~0x7);

        size_t sizeToPutBack = blockSize - aSize;

        int allocationStatus = (blockToInvestigate->header & PREV_BLOCK_ALLOCATED);

        mallocReturnAddr = (char *)((char *)blockToInvestigate + 8); //Return the payload 

        blockToInvestigate->header = aSize | THIS_BLOCK_ALLOCATED | allocationStatus; //We are unsure of what the previous block status is

        //Create new free block 

        sf_block *partitionedFreeBlock = (sf_block*)((char*)blockToInvestigate + aSize);
        partitionedFreeBlock->header = sizeToPutBack | PREV_BLOCK_ALLOCATED;

        size_t partitionedBlockSize = (partitionedFreeBlock->header & ~0x7);

        sf_footer *footerForPartition = (sf_footer*)((char*)partitionedFreeBlock + sizeToPutBack - 8);
        *(footerForPartition) = partitionedFreeBlock->header;

        //Delete the original free block and insert the new partitioned one

        int indexToDelete = findIndexFromMainFreeLists(blockSize);
        deleteBlockFromMainList(blockToInvestigate, indexToDelete);

        int indexToINsert = findIndexFromMainFreeLists(partitionedBlockSize);
        placeFreeBlockOfSizeX(partitionedFreeBlock, indexToINsert);

        
    }
    return mallocReturnAddr;
}

int errorCheckingForFreeandRealloc(void* pointer) {

    char *castToPointerChar = (char *)pointer;

    char *startOfHeap = ((char*)sf_mem_start() + 32); //We need to take prologue into consideration
    char *endOfHeap = ((char*)sf_mem_end() - 8); //We need to take epilogue into consideration

    sf_block *getHeader = (sf_block*)((char*)castToPointerChar - 8); //Access to header

    int allocationStatusOfThisBlock = (getHeader->header & THIS_BLOCK_ALLOCATED);
    int quickListStatusOfThisBlock = (getHeader->header & IN_QUICK_LIST);
    int prevAllocateBitStatus = (getHeader->header & PREV_BLOCK_ALLOCATED);

    char *addressOfHeader = (char *)getHeader;

    size_t getPointerBlockSize = (getHeader->header & ~0x7);

    sf_footer *getFooter = (sf_footer*)((char*)getHeader + getPointerBlockSize); //Access to footer, of an allocated block so its header + blocksize

    char *addressOfFooter = (char*)getFooter;

    if(castToPointerChar == NULL) return 1;
    if(((size_t)castToPointerChar & 0x7) != 0) return 1;
    if(getPointerBlockSize < 32) return 1;
    if((getPointerBlockSize & 0x7) != 0) return 1;
    if(allocationStatusOfThisBlock == 0) return 1; //Implies block has already been free'd


    //I could do more extensive error checking here, so I might come back to this later
    if(allocationStatusOfThisBlock == 1) { //Since this is an allocated block, check the heap start
        if(addressOfHeader < startOfHeap) return 1;
        if(addressOfFooter > endOfHeap) return 1;
    }


    if(quickListStatusOfThisBlock == 4) return 1;  //Implies the bit is turned on

    if(prevAllocateBitStatus == 0) { //Implies that the previous block is free

        sf_footer *getFooterFromPreviousBlock = (sf_footer*)((char*)getHeader - 8);
        size_t sizeOfBlock = (*getFooterFromPreviousBlock & ~0x7); //Dereference to get the value then bitmask

        sf_block *getHeaderOfPreviousBlock = (sf_block*)((char*)getHeader - sizeOfBlock);
        int checkAllocationStatus = (getHeaderOfPreviousBlock->header & THIS_BLOCK_ALLOCATED);

        if(checkAllocationStatus == 1) return 1; //This means that the block is allocated
        //But the previous block bit from the current block says it is not allocated

    }

    return 0;
}


// FUNCTIONS BEGIN HERE ***********
void *sf_malloc(size_t size) {

    if(size <= 0) return NULL; //No need to initialize the heap, not required to set sf_errno = ENOMEM cause no memory issue 

    int checkValue = checkMemStartMemEnd(); //First check if mem_start() == mem_end(), also implying we have a size > 0
    if(checkValue == 0) return NULL; //This means that somehow growHeap failed upon first initialzation of heap request, so we return NULL and sf_errno is already been set

    size_t aSize = makeMultipleOfAlignmentSize(size);

    //Search quick lists

    size_t minimumSize = 32;

    void * pointerToReturnAfterMalloc = NULL;

    //Check quick lists

    for(int i = 0; i < NUM_QUICK_LISTS; i++) {

        if(aSize == minimumSize) { //Must be the exact size 

            sf_block *returnedBlock = checkQuickListAtSpecificIndex(aSize, i);

            if(returnedBlock != NULL) {
                pointerToReturnAfterMalloc = (char *)(returnedBlock + 8);
                return pointerToReturnAfterMalloc;
            }
        }
        minimumSize += 8;
    }

    //Check main free lists

    int startingIndex = findIndexFromMainFreeLists(aSize);

    sf_block *blockToInvestigate = NULL;

    for(int i = startingIndex; i < NUM_FREE_LISTS; i++) {

        if(blockToInvestigate != NULL) break;

        sf_block *sentinelNode = &sf_free_list_heads[i];

        if(sentinelNode->body.links.next != sentinelNode) {

            sf_block *getDataBlocks = sentinelNode->body.links.next;

            while(getDataBlocks != sentinelNode) {

                //Get the header of the sentinel node 
                size_t blockSize = (getDataBlocks->header & ~0x7); //Since each block we put is going to be a header

                if(aSize <= blockSize) {

                    blockToInvestigate = getDataBlocks;
                    break;
                }

                getDataBlocks = getDataBlocks->body.links.next;

            }
        }
    }

    if(blockToInvestigate == NULL) { //Need to ask kernal for more memory

        sf_block *perceedingFreeBlock = sf_free_list_heads[7].body.links.next; //So that we hit the footer of the perceeding adjacent free block
        sf_block *tempNode = &sf_free_list_heads[7];
        sf_block *locationOfCoalescedBlock = NULL;
        size_t coalescedLocationSize = 0; //Set to 0 by deafult just in case

        int secondCallToMemGrow = 1;

        while (aSize > coalescedLocationSize) {

            char *growAgain = sf_mem_grow();

            if(growAgain == NULL) {
                sf_errno = ENOMEM;
                return NULL;
            }

            if(secondCallToMemGrow == 1) {

                secondCallToMemGrow += 1; //Increase so loop won't go back to here

                if(perceedingFreeBlock != tempNode) {

                    size_t adjacentFreeBlock = (perceedingFreeBlock->header & ~0x7);

                    //Get the allocation status of the block before this 
                    int allocationStatus = perceedingFreeBlock->header & PREV_BLOCK_ALLOCATED;

                    //Make the old epilogue into a header for the free space
                    sf_block *oldEpilogue  = (sf_block*)((char*)growAgain - 8);
                    oldEpilogue->header = PAGE_SZ;

                    size_t getEpSize = (oldEpilogue->header & ~0x7);

                    //Now coalesce the memory

                    perceedingFreeBlock->header = (adjacentFreeBlock + getEpSize) | allocationStatus; //Might be allocated or might not be allocated (the previous since we combined altogether)

                    size_t perceedingFreeSize = (perceedingFreeBlock->header & ~0x7);

                    //Set the footer of new coalesced free block

                    sf_footer *combinedFooter = (sf_footer*)((char*)perceedingFreeBlock + perceedingFreeSize - 8);
                    *(combinedFooter) = perceedingFreeBlock->header;
                    
                    //Set the epilogue

                    sf_block *setNewEpilogue = (sf_block*)((char*)sf_mem_end() - 8);
                    setNewEpilogue->header = 0x00000000 | THIS_BLOCK_ALLOCATED;

                    locationOfCoalescedBlock = perceedingFreeBlock;
                    coalescedLocationSize = locationOfCoalescedBlock->header & ~0x7;

                }
                else {
                    
                    sf_block *oldEP = (sf_block*)((char*)growAgain - 8);
                    oldEP->header = PAGE_SZ | PREV_BLOCK_ALLOCATED;

                    size_t oldEPSize = (oldEP->header & ~0x7);

                    sf_footer *footerForEP = (sf_footer*)((char*)oldEP + oldEPSize - 8);
                    *(footerForEP) = oldEP->header;

                    //Set new epilogue

                    sf_block *setNewEpilogue = (sf_block*)((char*)sf_mem_end() - 8);
                    setNewEpilogue->header = 0x00000000 | THIS_BLOCK_ALLOCATED;

                    //Add this to list? Yes
                    int indexOfInsertion = findIndexFromMainFreeLists(oldEPSize);
                    placeFreeBlockOfSizeX(oldEP, indexOfInsertion);

                    locationOfCoalescedBlock = oldEP;
                    coalescedLocationSize = locationOfCoalescedBlock->header & ~0x7;
            
                }

                if(aSize <= coalescedLocationSize) { //Size found, now check for splinter

                    blockToInvestigate = locationOfCoalescedBlock;

                    int splinterValue = checkForSplinter(blockToInvestigate, aSize);

                    pointerToReturnAfterMalloc = (char *)computeSplinter(splinterValue, blockToInvestigate, aSize);

                    return pointerToReturnAfterMalloc; //No need to loop any further
                }
                else  continue; //Force to the next loop
            }

            size_t internalSize = (locationOfCoalescedBlock->header & ~0x7);

            int previousAllocationStatus = internalSize & PREV_BLOCK_ALLOCATED; //IN the evenet this may be allocated

            //This is a free'd block so it has a footer
            locationOfCoalescedBlock->header = (internalSize + PAGE_SZ) | previousAllocationStatus;

            size_t internalSize2 = (locationOfCoalescedBlock->header & ~0x7);

            sf_footer *newFooter = (sf_footer*)((char*)locationOfCoalescedBlock + internalSize2 - 8);
            *(newFooter) = locationOfCoalescedBlock->header;

            sf_block *setNewEpilogue = (sf_block*)((char*)sf_mem_end() - 8);
            setNewEpilogue->header = 0x00000000 | THIS_BLOCK_ALLOCATED;

            coalescedLocationSize = (locationOfCoalescedBlock->header & ~0x7);
        }  

        blockToInvestigate = locationOfCoalescedBlock;

        int splinterValue = checkForSplinter(blockToInvestigate, aSize);

        pointerToReturnAfterMalloc = (char *)computeSplinter(splinterValue, blockToInvestigate, aSize);  

    }  
    else { //Only check splinterValue

        int splinterValue = checkForSplinter(blockToInvestigate, aSize);

        pointerToReturnAfterMalloc = (char *)computeSplinter(splinterValue, blockToInvestigate, aSize);

    }

    return pointerToReturnAfterMalloc; 
}

int coalesceFunction(sf_block *currentBlock);

void sf_free(void *pp) {
    
    int returnErrorValue = errorCheckingForFreeandRealloc(pp);

    if(returnErrorValue == 1) abort();

    sf_block *accessHeader = (sf_block*)((char *)pp - 8);
    size_t grabBlockSize = (accessHeader->header & ~0x7);

    size_t minimumSize = 32;

    //First check within the quick lists
    int sucessQuickList = 0;
    
    for(int i = 0; i < NUM_QUICK_LISTS; i++) {

        if(grabBlockSize == minimumSize) { //Must be the exact size

            sucessQuickList = insertIntoQuickList(accessHeader, i);
            break;
        }

        minimumSize += 8;
    }


    if(sucessQuickList == 1) return;

    //Then, we check the main free lists 
    coalesceFunction(accessHeader); //Coalesce with the main free_lists

    return;
}

//Will hopefully begin working on these two tomorrow ;-;

void *sf_realloc(void *pp, size_t rsize) {
    
    //Realloc is essentially going to be malloc again, but we change the size of a block 
    //We are also going to need to implement edge case checking for this function like we need to for sf_free()
    //We will come back later for error checking 
    //Case: Valid pointer but the size allocated is 0

    int returnErrorValue = errorCheckingForFreeandRealloc(pp);

    if(returnErrorValue == 1) {
        sf_errno = EINVAL;
        return NULL;
    }

    sf_block *getHeader = (sf_block*)((char*)pp - 8); 

    size_t getBlockSize = (getHeader->header & ~0x7);

    if(getBlockSize == (size_t)0) {

        sf_free((void *)pp); //We need to free the block
        return NULL;
    }

    //2 cases: reallocating to a larger size and reallocating to a large size
    //Case 1: Reallocating to a larger size

    //When we are doing realloc, the size that is inputted is the requested size
    //so we need to make sure that the requested size satisfies the minimum of 32 bytes
    //and if the requested size isn't aligned, then we need to make it aligned 
    //Thus, same procedure as malloc

    size_t rsizeModified = makeMultipleOfAlignmentSize(rsize);

    if(getBlockSize < rsizeModified) {

        void *pointerFromMalloc = sf_malloc(rsize); //We will send this because rsize will get aligned in the malloc call 

        if(pointerFromMalloc == NULL) return NULL;

        //If no null, then we need to use memcpy
        //We need to use memcpy, only copying the entire payload
        //Malloc will return the pointer address of the payload of an allocated memory, so we just want the payload 
        //To get the payload we can get the blocksize and subtract with 8, since 8 represents the size of the header
        //The difference in the values will be the payload 

        sf_block *getHeaderFromMallocCall = (sf_block*)((char*)pointerFromMalloc - 8);
        size_t getBlockValueFromMalloc = (getHeaderFromMallocCall->header & ~0x7); //Block size contains header + payload (with/without padding)
        size_t payloadSize  = getBlockValueFromMalloc - 8; //Remove the size of the header 

        memcpy(pointerFromMalloc, pp, payloadSize);

        //Now we need to free the original block 
        sf_free(pp);

        //Set this pointer that we made so that we can return it at the end 
        return pointerFromMalloc;

    }

    else if (getBlockSize > rsizeModified) { //Reallocating to a smaller size 

        //The case where we want to reallocate to a smaller size slightly varies
        //Because we are reallocating to a smaller size, we are going to be free'ing up 
        //some space. This means that we probably need to check for splinters

        //Case 1: If a splinter occurs, then we simply return the ptr
        //Case 2: If no splinter occurs, then we simply return the ptr 

        //Get the header so we can access the block size

        sf_block *getPPheader = (sf_block*)((char*)pp - 8);

        int investigateSplinter = checkForSplinter(getPPheader, rsizeModified);

        if(investigateSplinter == 1) return pp;

        else { //This means that a splinter is not going to happen, so we need to readjust

            size_t sizeDifference = getBlockSize - rsizeModified; //This is going to be the size of the free

            //Get to where we need to split the block
            //rsizeModified includes the header

            sf_block *getSplitLocation = (sf_block*)((char*)getHeader + rsizeModified);

            int statusOfPreviousBlock = (getHeader->header & PREV_BLOCK_ALLOCATED);

            //Change header so it reflects the new realloc size that was passed down
            getHeader->header = rsizeModified | THIS_BLOCK_ALLOCATED | statusOfPreviousBlock;

            //At the split location is where everything onwards is going to be the free'd
            //By everything onwards, we essentially mean the sizeDifference

            getSplitLocation->header = sizeDifference | THIS_BLOCK_ALLOCATED | PREV_BLOCK_ALLOCATED;
            //Make sure that the metadata for the heaer remain the same before splitting

            coalesceFunction(getSplitLocation); //Because we want this to go into the main free list, not the quick list

            return pp;
    
        }
    }
    else if (getBlockSize == rsizeModified) return pp; //The event where the malloc and realloc sizes that are given are the same 
    
    sf_errno = ENOMEM; //In the event the program reaches here, we set this to ENOMEM because ENOMEM hasn't been set before by malloc
    return NULL; //If some error occurs, we also return NULL;
}

void *sf_memalign(size_t size, size_t align) {

    //This function only works on already allocated blocks
    
    //We will first need to check if the alignment size is of power2
    //The alignment size must also 

    size_t acceptedAlignmentPrevious = 8;

    if(align < acceptedAlignmentPrevious) {
        sf_errno = EINVAL;
        return NULL;

    }

    if(((size_t)(align) & (size_t)(align - 1)) != 0) {
        sf_errno = EINVAL;
        return NULL;
    }

    //Getting here means the cases passed, so now we need to make a call to sf_malloc()
    //The call to sf_malloc() will add the 8 bytes that we are missing
    //No adding another + 8 because the footer is inside the payload
    size_t modifiedRequestedSize = size + align + 32; //Requested Size + Allignment Size + Minimum Block Size + Header/Footer size
    
    char *callToMalloc = (char *)sf_malloc(modifiedRequestedSize);

    if(callToMalloc == NULL) {
        sf_errno = ENOMEM;
        return NULL;
    }

    //If we are here, we now need to perform the adjustments
    //Previously, our allignment point was at the start of the payload
    //Now the goal to make sure that the start of the payload is at the new alignment mark

    sf_block *getHeaderFromMallocCall = (sf_block*)((char*)callToMalloc - 8);
    size_t getBlockSize = (getHeaderFromMallocCall->header & ~0x7); //Initial block size
    sf_block *getNextBlock = (sf_block*)((char*)getHeaderFromMallocCall + getBlockSize);

    //There are going to be 2 cases where we are needed to split: begining and the end 
    //Let's first check and see if the address that we got satisfies the alignment 

    if(((size_t)callToMalloc % align) == 0) return callToMalloc;  //The returned payload address
    //already satisfies the given alignment requirement, so do nothing


    //This is reached if the payload does not satisfy the alignment requirement
    //In that case we are going to have to constantly check until we find an address that works

    char *headerAddress = (char*)getHeaderFromMallocCall; //Gives us address to the header
    char *tempAddressToSavePayload = (char*)callToMalloc;
    //Our hunt for an address begins here

    size_t aSizeMemAlign = makeMultipleOfAlignmentSize(size); //Do this to get the actual size we need to allocate

    int addressFound = 0;

    while((size_t)tempAddressToSavePayload != (size_t)getNextBlock) {

        tempAddressToSavePayload += 1; //Increment address by 1 

        size_t grabSizeDifference = (size_t)tempAddressToSavePayload - (size_t)headerAddress; //From the beginning of the block

        if((((size_t)tempAddressToSavePayload % align) == 0) && grabSizeDifference >= 40) {
            //This means we have found our address that is also large enough, so we break
            //We want to check with a value of 40 for the purpose of meeting
            //the initial split off requirement to be at least 32 bytes
            addressFound = 1;
            break;
        }

    }

    //Means that within the block of memory, an address could not have been found so we return 
    if (addressFound == 0) {
        sf_errno = ENOMEM;
        return NULL;

    }

    //This part of the program is reached when we have found an address
    //First step to do is to find how much space we need to free up 
    //Remember: The split off portion needs to be of at least minimum block size 
    size_t getSizeToFreeUp = (size_t)tempAddressToSavePayload - 8 - (size_t)getHeaderFromMallocCall; //SUbtract 8 to consider the new header

    sf_block *newHeader = (sf_block*)((char*)tempAddressToSavePayload - 8);
    newHeader->header = (getBlockSize - getSizeToFreeUp) | THIS_BLOCK_ALLOCATED | PREV_BLOCK_ALLOCATED; //We have not free'd yet
    //size_t newBlockSize = (getBlockSize - getSizeToFreeUp);

    int preservePrevAllocBit = (getHeaderFromMallocCall->header & PREV_BLOCK_ALLOCATED);
    getHeaderFromMallocCall->header = getSizeToFreeUp | preservePrevAllocBit | THIS_BLOCK_ALLOCATED;

    sf_free(callToMalloc); //Free the unused space before the he new header

    if((newHeader->header & ~0x7) - aSizeMemAlign > 32) {

        //We can basically make a call to realloc to both modify and free the memory afterwards
        char *pointerReturned = (char*)sf_realloc(tempAddressToSavePayload, size); //Reallocates AND free's unused space after footer

        return pointerReturned;
    }
    else {

        return tempAddressToSavePayload;

    }
    //In the event the function is reached here
    sf_errno = ENOMEM;
    return NULL; //Just to satisfy the function's return type requirement 
}