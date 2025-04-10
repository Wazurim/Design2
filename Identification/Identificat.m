% Paramètres
nom_fichier = "identification_perturbation.csv";
ordre = 2;  % Nombre de pôles et de zéros
delai_max = 10; % Temps de retard maximal estimé (nombre d'échantillons)

data = importdata(nom_fichier);
%d1 = data(:,1);
%zero_list = zeros(10, 1);
%start_list = ones(10, 1) * 298;
%x = cat(1, zero_list, data(:,1));
%y = cat(1, start_list, data(:,3));
%u = cat(1, zero_list, ones(length(d1),1));

u = data(:, 2) - data(1, 2); % Soustrait le point d'operation
y = data(:, 3) - data(1, 3);

dat = iddata(y, u, 1);

delai_estime = delayest(dat);

[f_t, info] = tfest(dat, 1, 0, 0);

%f_t = tf([-8.9], [104 1]);
compare(dat, f_t);