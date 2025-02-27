function P = calculate_transition_matrix(sys,N)

% determine whether the system is continious or discrete-time
if(sys.Ts == 0)
    error('System is not discrete-time')
end

if isa(sys,'tf')
    sys = ss(sys);
end

A = sys.A;
B = sys.B;
C = sys.C;

% determine relative degree
transfun = tf(sys);
m = get_relative_degree(transfun);
% calculate the state transition matrix

P = zeros(N);
exponent_matrix = zeros(N);

for i = 1:N
    for j = 1:N
        markov_m = m + (i-1) - (j-1);
        if(markov_m < m)
            markov_m = NaN;
        end
        exponent_matrix(i,j) = markov_m;
        if(not(isnan(markov_m)))
            P(i,j) = C*A^(markov_m-1)*B;
        else
            P(i,j) = 0;
        end
    end
end
end
