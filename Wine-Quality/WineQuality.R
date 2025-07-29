## Imports
library(neuralnet)

 # import wine quality csv data
head(winequality.red)
sum(is.na(winequality.red))

wq <- winequality.red[, -12]
wq$qual <- factor(ifelse(winequality.red$quality >= 7, 1, 0))
str(wq)
table(wq$qual)

wq_x <- scale(wq[,-12])
wq_y <- wq$qual

set.seed(395)
ind4 <- sample(1:nrow(wq), 0.75*nrow(wq), replace=F)
train_x <- wq_x[ind4,]
train_y <- wq_y[ind4]
test_x <- wq_x[-ind4,]
test_y <- wq_y[-ind4]

train_scaled <- data.frame(train_x, train_y)
test_scaled <- data.frame(test_x, test_y)
str(train_scaled)
str(test_scaled)

 # determine number of neurons to use in hidden layer
B <- 20
train_err_vec4 <- numeric(B)
test_err_vec4 <- numeric(B)
for (i in 1:B){
  nn <- neuralnet(train_y ~ ., train_scaled, hidden=i, err.fct="ce", act.fct="logistic",
                  linear.output=F, stepmax=10^8)
  
  pred_train4 <- predict(nn, newdata=train_scaled, type="response")
  yhat_train4 <- round(pred_train4[,2])
  train_err_vec4[i] <- mean(train_scaled$train_y != yhat_train4)
  
  pred_test4 <- predict(nn, newdata=test_scaled, type="response")
  yhat_test4 <- round(pred_test4[,2])
  test_err_vec4[i] <- mean(test_scaled$test_y != yhat_test4)
}

plot(1:B, test_err_vec4, type='l', col='red', ylim=c(min(train_err_vec4), max(test_err_vec4)),
     xlab="Number of neurons", ylab="Misclassification error")
lines(1:B, train_err_vec4, col='blue')
legend("right", legend=c("Test error", "Training error"), col=c("red", "blue"),
       lwd=2)

M <- 4
test_err_vec4[M]
train_err_vec4[M]

nn_best <- neuralnet(train_y ~ ., train_scaled, hidden=M, err.fct="ce", act.fct="logistic",
                     linear.output=F, stepmax=10^8)
plot(nn_best)
prediction(nn_best)

 # compare to logistic regression
lr_fit4 <- glm(train_y ~ ., data=train_scaled, family="binomial")

yhat_lr_train <- round(predict(lr_fit4, newdata=train_scaled, type="response"))
yhat_lr_test <- round(predict(lr_fit4, newdata=test_scaled, type="response"))
(train_err_lr <- mean(yhat_lr_train != train_scaled$train_y))
(test_err_lr <- mean(yhat_lr_test != test_scaled$test_y))
summary(lr_fit4)



