
s=tf('s');
syms z

%G1=0.48/(1+104*s)

%G2=(0.79*exp(-4*s))/(1+30*s)

%G3=(0.88*exp(-2*s))/(1+30*s)

%G4=-0.000014/(1+0.077*s)

%G5=-3.57

%G6=8/(1+0.00998*s)

%Gc = 0.44185/(50.859*s+1) 



%G7=13653.3

%G8=1/65536

%Gproc = G1*G2*G3*G4*G5*G6

%Gproc_discret = c2d(Gproc,1)

%Gcd = c2d(Gc,1)

F =(1*exp(-12*s))/(1+77*s)^2
Gcd = c2d(F,1)
syms z
ilaplace(Gcd)