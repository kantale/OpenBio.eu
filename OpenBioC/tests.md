
This is a list of possible tests. In the future we will build selenium auto tests.

1. Empty WF . Add Description, Website --> Save. Name: WF1 
2. Empty WF . Add Description, Website --> Drag n Drop WF1 . Name: WF2 . Confirm that it is plotted correctly 
3. Empty Wf . Add Description, Website --> Drag n Drop WF2 . Name: WF3
4. Empty Wf . Add Description, Website --> Drag n Drop WF3 . Name: WF4
5. Empty Tool. Save . Name T1/1
6. Empty WF . Add T1/1 -> Name WF5
7. Empty WF .  Add Description, Website --> Drag n Drop WF5 . Name: WF6
8. Empty Tool. Add dependent T1/1 . Name T2/1
9. Empty WF . Drug n Drop T2 . Name WF7
10. Empty WF . Add Dependency WF7 . Save WF8
11. Empty Tool . Add dendent T2 . Add Variables var1, var2. Name T3/1
12. Empty WF . Add T3 . Add input_var, output_var. Add Step1(Uses input_var, output_var),  Step2(T3/1/var1, calls Step1). WF9
13. Empty WF . DnD WF9 . Save WF10




