% Paramètres
nom_fichier = "test_data.txt";
ordre = 2;


data = importdata(nom_fichier);

x = data.data(:,1);
y = data.data(:,2);
u = data.data(:,3);


dat = iddata(y, u);

tf = tfest(dat, ordre);

compare(dat, tf);