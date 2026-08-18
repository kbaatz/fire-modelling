# Fire Model

These programs are variations of the Drossel and Schwabl model for forest fires. The models are a type of cellular automata where each cell is one of three states (EMPTY, TREE, ON-FIRE). 
A tree grows with the probability of p in an empty square and a square occupied by a tree catches fire with the probability f. Rather than accurately simulating forest fires, the Drossel and Schwabl models were created to explore
dynamical systems that display self-organized criticality. The first model, model.py, is faithful to the original model and can display certain patterns such as the steady growth of fire spirals.
I used [Christian Hill's model](https://scipython.com/blog/the-forest-fire-model/) as a basis for my code. In following iterations (model2.py and model3.py) I add features that immitate the influence
of wind angle and intensity and different species on burn patterns. In the final model, one can observe more realistic mosiac style burn patterns amongst conifers and hardwoods and see how wildfires
affect the tree population after several growth and burn cycles. 


## Sources
[Wikipedia Forest-fire Model](https://en.wikipedia.org/wiki/Forest-fire_model)

[Self Organized Critical Forest-fire Model, B. Drossel and F. Schwabl](https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.69.1629)


[How different species affect fire intensity](https://smokedsystem.com/how-different-tree-species-affect-fire-intensity/#Fire_Intensity_and_the_Science_Behind_How_Forests_Burn) 


[The Forest-fire Model, Christian Hill](https://scipython.com/blog/the-forest-fire-model/)
