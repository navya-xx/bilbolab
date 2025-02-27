function K = eigenstructure_assignment(A,B,P,V)
K = [];
N = size(A,1);
M = size(B,2);


reduced_ev = cell(N,1);
D = cell(N,1);

for i = 1:N
    reduced_ev{i} = V(not(isnan(V(:,i))),i);
    D_i = zeros(M,N);
    
    V_temp = V(:,i);
    V_temp(V_temp == 0 | V_temp == 1) = 1;
    V_temp(isnan(V_temp)) = 0;
    
    indexes = find(V_temp,M);
    for j = 1:M
        D_i(j,indexes(j)) = 1;
    end
    D{i} = D_i;
end

b = cell(N,1);
x = cell(N,1);
r = cell(N,1);
for i = 1:N
    b{i} = inv([A-P(i)*eye(N),B; D{i}, zeros(M)]) * [zeros(N,1); reduced_ev{i}];
    x{i} = b{i}(1:N);
    r{i} = -b{i}(N+1:N+M);
%     disp(i);
%     disp(b{i});
end


for i = 1:N
   X(:,i) = x{i};
   R(:,i) = r{i};
end

K = real(R*inv(X));

if(any(isnan(K)))
   error("Unable to find proper eigenstructure!"); 
end

end