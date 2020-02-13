
# Tests
## Tools 
1. Create tool test empty installation. Create WF test. Add tool test. Save. Edit tool test installation. Download test WF. Edits should be visible on bash script of WF 🆗  
2. Create tool test/1. Create WF test/1. Add tool test/1 to WF. Save test/1. Create tool test/2. Add tool test/2 as dependency to test/1. Go to WF test/1. Graph should be updated 🆗  
3. Create tool test/1. Create WF test/1. Add tool test/1 to WF. Save test/1. Create tool test/2. Add tool test/2 as dependency to test/1. Make an edit at installation instructions of test/2. Go to WF test/1 and download bash. Edit should be be visible. 🆗 
4. Create tool test/1 and save. Create tool test/2 and add test/1 as a dependency. Make an edit at test/1 . test/1 should still be a dependency of test/2. 🆗 
5. Create tool test/1 and save. Create tool test/2 and add test/1 as a dependency. Create WF test/1 and add test/2 and save. Edit tool test/1 and remove test/2 from dependency. Graph of WF test/1 should be updated 🆗 
6. Create tool test/1. Create tool test/2 add test/1 as dependency. Try to delete tool test/1. There should be an error message. 🆗 
7. Create tool test/1. Create WF test/1 add tool test/1. Try to delete tool test/1. There should be an error message. 🆗 
8. Create tool test/1 with variable A. Create tool test/2 with dependency tool test/1. Create WF test/1 and use variable A from main_step. Edit test/2 and remove test/1 as a dependency. Check WF test/1. The edge from main_step to variable A must have been deleted. 🆗 

## WFs
9. Create WF test/1 . Create WF test/2 and add WF test/1. Edit WF test/1 and add a step new_step. Check WF test/2, the new step should be on the graph. 🆗  
10. Create a WF test/1 and add a new step new_step. Create WF test/2 and add WF test/1. Edit WF test/1 and delete step new_step. Check WF test/2 the step new_step must have been deleted. 🆗 

## Forks
11. Create tool test/1/1. Fork tool test/1/1 and create tool test/1/2. Delete tool test/1/1. On the search jstree tool test/1/2 should be on the root. 🆗 
12. Create the fork tree with tools: test/1/1 --> test/1/2 --> test/1/3. Delete tool test/1/2. The fork tree now is test/1/1 --> test/1/3. 🆗 
13. Create fork tree with WFs. test/1 --> test/2. Delete test/1. test/2 should be on the root. 🆗 
14. Create fork tree with WFs. test/1 --> test/2 --> test/3. Delete test/2. The new tree should be tree/1 --> tree/3. 🆗 

## Finalizing
15. Create tool test/1. Finalize it. It should not be editable. 🆗 
16. Create tool test/1. Create tool test/2 and add test/1 as a dependency. Try to finalize test/2. An error should appear "This tool cannot be finalized. It depends from 1 draft tool(s). For example: test/1/1" 🆗 
17. Same as check 16. Finalize tool test/1 . Now we should be able to finalize tool test/2. 🆗 
18. Create WF test/1 . finalize WF test/1. WF test/1 should not be editable. 🆗 
19. Create WF test/1. Create WF test/2 and add test/1. Try to finalize WF test/2 . An error should appear "This workflow cannot be finalized. It contains 1 draft workflow(s). For example: test/1"
20. Same as check 19. Finalize WF test/1. On WF Test/2 node for test/1 changes color (🆗). Finalize WF test/2.  This should be possible 🆗 
21. Create tool test/1. Create WF test/1 and add tool test/1. Try to finalize WF test. An error should appear: "This workflow cannot be finalized. It contains 1 draft tool(s). For example: test/1/1" 🆗 
22. Create tool test/1. Create WF test/1 and add tool test/1. Finalize tool test/1. The node graph in WF test/1 for tool test/1 changes (🆗) . Finalize WF test/1. This should be possible. 🆗 
23. Create tool test/1. Create tool test/2 and add test/1 as dependency. Create WF test/1 and add tool  test/2.  The following should be possible: Finalize tool test/1. Graph on WF test/1 updates. Finalize tool test/2. Graph on WF test/1 updates. Finalize WF test2. 🆗  

## Additional tests
24. Create WF test/1. Create WF test/2 add WF test/1. Create WF test/3 add WF test/2. 
   * Edit WF test/2 add new step new_step2. Graph on WF test/3 changes. 🆗 
   * Edit WF_test/2 remove step new_step2. Graph on WF_tet/3 changes. 🆗 
   * Finalize on this and only on this order: WF test/1 , WF test/2 , WF test/3. 🆗 


## Tool Variables
25. Create Tool test/1. Create WF test/1 add tool test/1. Edit Tool test/1 add variable var1. Edit WF test/1 and edit main_step. var1 of tool test/1 should be visible in ACE suggestions. 🆗 

26. Create WF test/1. Add step step2. Call step2 from main_step. Save WF. Edit WF. Click main_step. Press UPDATE. Edge main_step --> step2 should remain. 🆗 
27. Create WF test/1. Add step step2. Call main_step from from step2. Save WF. Edit WF. Click main_step. Press Update. Edge step-->main_step should remain. 🆗 

28. (Disconnect). Create workflow test/1. Create WF test/2 and add WF test/1 and save. Create WF test/3 and add WF test/2. Edit WF test/2 and disconnect test/1 save. Edit WF test/1 and add a new step s2. Check WF test/2 it should NOT contain the new step. Check WF test/3 in SHOULD contain the new step. 🆗




