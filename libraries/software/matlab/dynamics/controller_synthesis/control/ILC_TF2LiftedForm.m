function [liftedFormMatrix] = ILC_TF2LiftedForm(transferFunction,nbrOfSamples, relativeDegree)
% This function calculates the lifted form matrix of a proper transferFunction.
%
% The first input argument is the transfer function.
% The second input argument is the number of samples in a trial. Bristow
% denotes this with N.
% The third input argument is the system's relative Degree. Bristow denotes
% this with m.
%
% The output is the lifted form matrix.

    N = nbrOfSamples;
    m = relativeDegree;

    imp    = zeros(N+m,1);
    imp(1) = 1;
    imp_response     = lsim(transferFunction, imp);
    tm = toeplitz(imp_response(1+m:end));
    liftedFormMatrix = tril(toeplitz(imp_response(1+m:end)));
end