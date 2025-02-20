% Paramètres
nom_fichier = "thermistance3_temp_1000sec_0_001Ratio.txt";
ordre = 2;  % Nombre de pôles et de zéros
delai_max = 10; % Temps de retard maximal estimé (nombre d'échantillons)

data = importdata(nom_fichier);
d1 = data(:,1);
zero_list = zeros(10, 1);
start_list = ones(10, 1) * 298;
x = cat(1, zero_list, data(:,1));
y = cat(1, start_list, data(:,2));
u = cat(1, zero_list, ones(length(d1),1));

dat = iddata(y, u);

delai_estime = delayest(dat);

[tf, info] = tfest(dat, ordre, ordre-1, 'InputDelay', delai_estime);

compare(dat, tf);