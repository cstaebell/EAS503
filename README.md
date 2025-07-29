# Data Science Portfolio
## Renewable Energy Perspectives
Global electricity data was sourced from Ember for this exercise in data-driven storytelling. Data was manipulated and visualized using pandas, matplotlib, and seaborn. An accompanying writeup places the analysis within the context of current events and discusses key insights gained from data exploration. 

## Coffee Shop Sales
Python visualizations and SQL queries (SQLite) were leveraged to gain operational insights for a simulated coffee shop sales dataset. A companion article discusses the findings and their significance for our fictitious coffee shop. 

## Income Dataset Neural Network

## Fashion MNIST Convolutional Neural Network


## Wine Quality: Predictive Performance of Logistic Regression vs. Neural Network
This project was implemented in R with the goal of predicting wines with a quality rating of 7 or higher based on 11 chemical predictors. One hundred neural networks with single layer neuron numbers ranging from 1 to 20 were created and the holdout method was used to determine the best number of neurons in the hidden layer. The starting values for the weights of each neural network were randomly set by R. When using 4 neurons, the training misclassification rate was 7.51% and the test misclassification rate was 12.75%.

Logistic regression attained a training error rate of 11.09% and a test error rate of 13.25%. This test error rate is a half a percentage point higher than that obtained using the neural network. Despite the slightly better performance, the neural network has some drawbacks. The optimization process for selecting the number of neurons in the hidden layer took a while (especially when initially tested with larger numbers) and is not very stable. That is, different numbers of neurons were observed to minimize the test error when the loop was run multiple times. Further, the neural network is not very interpretable.

Overall, logistic regression appears to be the preferred method for this application. It offers predictive
accuracy comparable to the neural network and has the additional advantage of interpretability.
