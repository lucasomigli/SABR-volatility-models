# Master Thesis project files for the completion of the MSc in Mathematical Finance at Birkbeck College of London.

### Main Objective
Main question: How accurate are the new stochastic volatility models that are currently used in financial institutions and by professionals with respect to calculating implied volatility? 
A research that will go trogh a bried history of implied volatility over the last decades, as well as a in depth statistical research on effectiveness on models such as the Heston stochastic volatility, SABR free, normal and shifted models. Graphical and statistical analysis of the models using volatility smiles and surfaces.
To add to the main topic, how good are these models with respect to negative interest rates environonments?

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
- Introduction. Outline the main question of the research, therefore identify the objective and the main issues and fixes. What is the contribution to the academic world that this paper sets its objective to? In this case, the paper wants to identify how different these models are woth respect to the actual process and how "good" they are with respect to modelling volatility in Ameirican equity indeces (specifically Nasdaq and SPX). 
- Literature Review. Reference all the papers I printed out. Explain in detail what are the issues that have been arising in the latest period with respect to modelling future volatilities. Models have grown since the first Black model, but professionals and institutions still rely on ancient methods to understand volatility smiles. Go trough pros and cons on each model. Explain how for example the Heston model was the first real effective stochastic model that comes close enough to market volatilities with a huge downside, the complications of modelling trough a complex set of functions that increase the computational costs (both time, power and consumptions)
- Mathematical Definitions.
    - General Assumptions.
    - Ito's Calculus
    - Pricing under the risk-neutral measure
- Theory And Methodology: An history of volatility, from constant to stochastic
    - Bachelier's Normal model. The imporant features of the latter model for the Normal model in later implications for sthochastic volatility models.
    - Black Model. 
    - Implied Volatility Under Black-Scholes.
    - Volatility Smiles and Skews.
    - Volatility Surfaces.
    - Constant Elasticity of Variance
    - Dupire Local Volatility 
    - Stochastic Volatility and the Heston Model. Finally a first stochastic volatility model, which opens the gate to more realistic volatility smiles. The Heston model also has a additional constrains, discovered by Feller, which constricts the variance to be strictly positive. The objective function minimizes the squared difference between prices observed in the market and prices calculated from the model. We minimise using a plethora of different algorithms which effectively use gradient methods to solve. Explain, mentioning source, all the different minimisation algorithms with their pros and cons. Difficulty of finding the right variables due to a huge bias in choosing initial conditions, leading to higher computational times. 
    - SABR models. Hagan's formula first gave a push to the new models which still to this day are used in most situations, especially within interest rates derivatives. A more complex and solid framework which more realistically prices options based on volatility of alpha, beta, rho and sigma. We first calibrate the model either using the 1st (directly computing the parameters) or 2nd method (calculating the alpha based on rho and nu. Different new variants contributed overtime to the original model, with a few dealing also with negative interest rates. In total we have the normal SABR model (explain importance of the Bachelier Normal model), the shifted SABR, the Floch-kennedy variant and the mixture and free boundary SABR. 
    SABR models. Differences between normal, shifted and Floch-Kennedy together with the two calibration methods and beta.
    - SABR Calibration.
    - Normal SABR. General explanation of calibration process. Plots, graphs and the Backbone behaviour of smiles.
    - Shifted SABR.
    - Floch-Kennedy SABR. 
    - (mention) Free Boundary SABR, Obloj's refinement and mixture models.
    - Beyond SABR models, negative interest rates and issues. Hagan's formula and SABR models have opened the gate for pricing under a negative rates economy. Being a rising major issue in the last two decades, we now have something to work with. Talk about models used in case of negative interest rates: shifted SABR, free-boundary SABR, Bachelier model.
    - (mention) Stochastic local volatility models.
    - (mention) Monte Carlo implied volatility calculations.
- Analysis And Results on SP500 and Nasdaq. Statistical testing for errors with respect to variance, plot volatility surfaces and smiles and visualise the differences. 
    - Graphic comparison ov volatility smiles under different models and tenors.
    - MSE comparisons.
    - Implied price differentials.
    - PDF of volatility implied by each model.
- Conclusion. Identify pros and cons of each model and define which model is most approrpiate for equity indeces. Do the theretical expectations congrue with the statistical outputs? Explain. 
    
------

### Notes
- Write a solid theoretical explanation of the models history and growth since Black's 1976 model up to modern days. Identify problems related to old models and see how the new entrances have been fixing them.
- Could mention the 2008 crysis as a way to enphatise the fault of using volatily models which were based on simplest, unrealistic Black and Scholes models.
- Whereas most essays talk about the free boundary SABR model or the Local Volatility models, due to difficulties in creating related surfaces in QuantLib, focus more on the Floch-Kennedy variant or the shifted SABR. It would be great to mention the theory behind Obloj's refinement and new stochastic local volatility models as well as mixture models.
- Uses of SABR models in negative interest rates environments. 
- What is the difference, statistically and numerically, between the normal and shifter variants of the SABR model?
- Mention difficulties in calibrating the Heston model with respect to choosing initial conditions appropriately
- Implied volatility VS local volatility VS realised volatility. What are we trying to replicate the most?