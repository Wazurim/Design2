clear
% Lire les données du csv
addpath("support")
%res = read_csv("essaie2_temp");
data = importdata("essaie2_temp.txt");
temps = data(:,1);
u = data(:, 2);
t1 = data(:, 3);
t2 = data(:, 4);
t3 = data(:, 5);
% Récupérer les vecteur
%t1 = res.Temp_0__C_;
%t2 = res.Temp_1__C_;
%t3 = res.Temp_2__C_;
%temps =  res.Temps_s_;
%u = res.Echelon_V_;

hold on
plot(temps, t1);
plot(temps, t2);
plot(temps, t3);


%% Idenfication de h

% Température expérimentale pendan l'essaie de laché
indice_lache = 1027;
fin = 2000;
temps_exp = temps(indice_lache:fin, 1) - temps(indice_lache, 1);
t_exp1 = t1(indice_lache:fin, 1);
t_exp2 = t2(indice_lache:fin, 1);
t_exp3 = t3(indice_lache:fin, 1);

%T_piece = t3(26, 1);
T_piece = 23.8;


function [h_fit] = find_h(T_exp, temps_exp, T_piece, display)
    % Définition d'un élément dV
    dx = 1*10^-3; % Longueur en mètres
    dy = 1*10^-3; % Largeur en mètres
    dz = 1.6*10^-3; % Épaisseur en mètres

    % Paramètres matériels
    rho = 2700; % Densité de l'aluminium (kg/m³)
    cp = 897; % Capacité thermique massique en J/kg.K

    % Surface totale en contact avec l'air
    A_eff = 2 * (dx * dy); % Surface totale d'échange
    dV = dx * dy * dz; % Volume de la plaque
    T0 = T_exp(1);
    Ta = T_piece;

    cooling_model = @(h, t) Ta + (T0 - Ta) * exp(-h * A_eff / (rho * cp * dV) * t);
    h0 = 10; % Valeur initiale pour h
    h_fit = lsqcurvefit(cooling_model, h0, temps_exp, T_exp);

    if display == true
        t_fit = linspace(0, max(temps_exp), 100);
        T_fit = cooling_model(h_fit, t_fit);
        fprintf('Le coefficient de convection estimé est h = %.2f W/m²K\n', h_fit);
        figure;
        plot(temps_exp, T_exp, 'm.', 'MarkerFaceColor', 'r'); % Données expérimentales
        hold on;
        plot(t_fit, T_fit, 'b-', 'LineWidth', 2); % Modèle ajusté
        xlabel('Temps (s)');
        ylabel('Température (°C)');
        legend('Données expérimentales', 'Estimation');
        title('Estimation de la convection selon les données expérimentales');
        grid on;
    end
end

find_h(t_exp1, temps_exp, T_piece, true)