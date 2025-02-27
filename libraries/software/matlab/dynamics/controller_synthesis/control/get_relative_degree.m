function relative_degree = get_relative_degree(transfun)

% if the system is discrete-time, first convert it to continious time
if(transfun.Ts > 0)
   transfun = d2c(transfun,'zoh');
end

if(isa(transfun,'ss'))
    transfun = tf(transfun);
end

denominator = transfun.Denominator;
numerator = transfun.Numerator;
relative_degree = get_degree(denominator) - get_degree(numerator);
end


function out = get_degree(polynomial)

polynomial = polynomial{1};

i = 0;

while(polynomial(i+1) == 0)
    i = i+1;
end

out = length(polynomial)-i;

end