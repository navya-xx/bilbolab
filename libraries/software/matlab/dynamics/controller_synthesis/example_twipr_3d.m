clear all;
clc;
close all;

mode = 'nonlinear';


% State: [s, v, theta, theta_dot, psi, psi_dot]

robot = TWIPR_Dynamics_3D(0.01);
poles = [0 -20 -3+1i -3-1i 0 -1.5];
% 
eigenvectors = [   1,      nan,    nan,    nan,    0,    nan;
    nan,    1,    nan,    nan,    nan,    nan;
    nan,    nan,    1,      1,        nan,    0;
    nan,    nan,    nan,    nan,    nan,      nan;
    0,      nan,      nan,    nan,    1,      1;
    nan,    0,      0,      0,    nan,    nan;
    ];
robot.set_eigenstructure(poles,eigenvectors);

% robot.set_reference_controller_pitch(-1.534/2,-2.81/2,-0.07264/2,2);
% robot.set_reference_controller_yaw(-0.3516,-1.288,-0.0002751,6)

% u = ones(2,5*50).*[1;-1]; % Set the reference for xdot to 1 for the whole simulation

u = ones(2,250); % Set the reference for xdot to 1 for the whole simulation
[y,x] = robot.simulate(u,mode,[0 0 0 0 0 0]'); % simulate the whole timeseries at once

% to demonstrate the ability to simulate one step each, first reset the
% state of the controller and the robot
robot.reset_ctrl();
robot.set_state(robot.x0);
robot.set_state([0 0 0 0 0 0]');

state = 3;
stairs(x(state,:));
hold on;
