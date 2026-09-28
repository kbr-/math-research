\\ Forced relations among squared spans: dim G_{2c}(F_3^v) = coefficient of t^{2c} in (1+t+t^2)^v.
\\ For W's parameters |F| <= n^{K+1} = e^{0.4c}; counting forces relations inside a v-space only if dim < |F|.
\\ Prints, for c = 50, 100, 200, the largest v with log(dim) < 0.4c, its ratio v/c, and log(dim) at v = 2c.
for(i=1,3, c=[50,100,200][i]; best=0; forstep(v=c,3*c,1, d=polcoef((1+t+t^2)^v, 2*c, t); if(d>0 && log(d) < 0.4*c, best=v)); \
  print("c=", c, ": largest v with log dim G_2c(F_3^v) < 0.4c is v=", best, " (ratio ", best*1.0/c, "); log dim at v=2c: ", log(polcoef((1+t+t^2)^(2*c), 2*c, t))));
quit
