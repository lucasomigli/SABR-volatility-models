# Master Thesis project files for the completion of the MSc in Mathematical Finance at Birkbeck College of London.

### Main
- [] Plot implied option prices against market prices with respect to each model
- [] Organise thesis theoretical structure. Write down general concept
- [] Test using negative interest rates
- [] Write a clear, non-empirical statistical process for comparing models

### Optional
- [] Add Obloj's refinement model for SABR
- [] Dupire's Local Volatility Model Surface (now returning negative variance)
- [] Add Free Boundary SABR model and/or mixed SABR models
- [] Add visualised PDF for each model 

--------------------

### Thesis tree structure 

- Abstract.
- Introduction.
- Literature Review.
- Data And Methodology.
    - Data.
    - Methodology.

------

### Notes
- Write a solid theoretical explanation of the models history and growth since Black's 1976 model up to modern days. Identify problems related to old models and see how the new entrances have been fixing them.
- Could mention the 2008 crysis as a way to enphatise the fault of using volatily models which were based on simplest, unrealistic Black and Scholes models.
- Whereas most essays talk about the free boundary SABR model or the Local Volatility models, due to difficulties in creating related surfaces in QuantLib, focus more on the Floch-Kennedy variant or the shifted SABR. It would be great to mention the theory behind Obloj's refinement and new stochastic local volatility models as well as mixture models.
- Uses of SABR models in negative interest rates environments. 
- What is the difference, statistically and numerically, between the normal and shifter variants of the SABR model?
- Mention difficulties in calibrating the Heston model with respect to choosing initial conditions appropriately
- Implied volatility VS local volatility VS realised volatility. What are we trying to replicate the most?