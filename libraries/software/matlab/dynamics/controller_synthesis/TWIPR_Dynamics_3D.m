classdef TWIPR_Dynamics_3D < handle
    properties
        
        m_b = 2.5; % Mass of Body
        m_w = 0.636; % Mass of one or two wheels
        l_cg = 0.026; % Distance CG to wheel axis
        d_wheels = 0.28; % Distance between the wheels
        I_wheels = 5.1762e-4; % MOI of one wheel
        I_y = 0.01648; % MOI for pitching
        I_x = 0.02; % MOI for turning around x -> please look in Dennis Thesis how he did it
        I_z = 0.03; % MOI for turning around z -> only guessed -> please look in Dennis Thesis how he did it
        c_alpha = 4.6302e-4; % just leave it like this
        r_w = 0.055; % radius of wheels
        
        tau_theta = 0; % don't change for now
        tau_x = 0; % don't change for now
        
        Ts
        
        % models
        
        % state space matrices
        A, B, C, D, A_hat
        A_d,B_d,C_d,D_d,A_hat_d
        
        % state-space systems
        sys_cont
        sys_discrete
        
        % states
        state = [0 0 0 0 0 0]';
        x0 = [0 0 0 0 0 0]';
        
        % controllers
        K_discrete = [0 0 0 0 0 0;0 0 0 0 0 0]; % state feedback matrix
        K_cont = [0 0 0 0 0 0;0 0 0 0 0 0];
        
        ref_ctrl_is_set = false
        
        P_pitch = 0
        I_pitch = 0
        D_pitch = 0
        
        P_yaw = 0
        I_yaw = 0
        D_yaw = 0
        
        last_error_pitch = 0
        integral_pitch = 0
        last_error_yaw = 0
        integral_yaw = 0
        
        pitch_ref_ctrl_num
        yaw_ref_ctrl_num        
    end
    
    methods
        
        % @brief: initializes the object
        function obj = TWIPR_Dynamics_3D(Ts,x0)
            
            if(nargin>1)
                obj.x0 = x0;
            end
            
            obj.state = obj.x0;
            obj.Ts = Ts;
            
            % calculate the linear model matrices
            [obj.A,obj.B,obj.C,obj.D] = obj.get_model_linear_3d();
            
            % make the linear continious time model
            
            states = {'x' 'x_dot' 'theta' 'theta_dot' 'psi' 'psi_dot'};
            inputs = {'M_L','M_R'};
            outputs = {'theta'};
            obj.sys_cont = ss(obj.A,obj.B,obj.C,obj.D,'statename',states,'inputname',inputs,'outputname',outputs);
            obj.sys_discrete = c2d(obj.sys_cont,obj.Ts);
            obj.A_d = obj.sys_discrete.A;
            obj.B_d = obj.sys_discrete.B;
            obj.C_d = obj.sys_discrete.C;
            obj.D_d = obj.sys_discrete.D;
            
            obj.A_hat = obj.A;
            obj.A_hat_d = obj.A_d;
        end
        
        % set_state
        % @brief set's the state of the dynamic model to the given state
        function set_state(obj,state)
            obj.state = state;
        end
        
        function reset_ctrl(obj)
            obj.last_error_pitch = 0;
            obj.last_error_yaw = 0;
            obj.integral_pitch = 0;
            obj.integral_yaw = 0;
        end
        
        
        function [y_out,x_out] = simulate_step(obj,u,mode)
            if strcmp(mode,'linear')
                [y_out,x_out] = obj.simulate_step_linear(u);
            elseif strcmp(mode,'nonlinear')
                [y_out,x_out] = obj.simulate_step_nonlinear(u);
            else
                error('Wrong mode selected!');
            end
        end
        
        % simulate
        % @brief simulates the model with the given input vector. If a x0
        % is given it starts from x0, otherwise from the state of the
        % dynamic model
        function [y_out,state_out] = simulate(obj,u,mode,x0)
            if(nargin>3)
                obj.state = x0;
            end            
            if(strcmp(mode,'linear'))
                [y_out,state_out] = obj.simulate_linear_model(u);
            elseif(strcmp(mode,'nonlinear'))
                [y_out,state_out] = obj.simulate_nonlinear_model(u);
            else
                error('Wrong mode selected!');
            end
        end
        
        function set_reference_controller_pitch(obj,Kp,Ki,Kd,state_num)
            obj.P_pitch = Kp;
            obj.I_pitch = Ki;
            obj.D_pitch = Kd;
            obj.pitch_ref_ctrl_num = state_num;
            obj.ref_ctrl_is_set = true;
        end
        
        function set_reference_controller_yaw(obj,Kp,Ki,Kd,state_num)
            obj.P_yaw = Kp;
            obj.I_yaw = Ki;
            obj.D_yaw = Kd;
            obj.yaw_ref_ctrl_num = state_num;
            obj.ref_ctrl_is_set = true;
        end
        
        
        % set the eigenstructure
        function set_eigenstructure(obj,P,V)
            
            states = {'x' 'x_dot' 'theta' 'theta_dot' 'psi' 'psi_dot'};
            inputs = {'M_L','M_R'};
            outputs = {'theta'};
            
            obj.K_cont = eigenstructure_assignment(obj.A,obj.B,P,V);
            obj.K_discrete = eigenstructure_assignment(obj.A_d,obj.B_d,exp(P*obj.Ts),V);
            
            obj.A_hat = (obj.A-obj.B*obj.K_cont);
            obj.sys_cont = ss(obj.A_hat,obj.B,obj.C,obj.D,'statename',states,'inputname',inputs,'outputname',outputs);
            
            obj.A_hat_d = (obj.A_d-obj.B_d*obj.K_discrete);
            obj.sys_discrete = ss(obj.A_hat_d,obj.B_d,obj.C_d,obj.D_d,obj.Ts,'statename',states,'inputname',inputs,'outputname',outputs);
        end
        
    end
    %% private methods
    methods (Access = private)
        % --------------------------------------------------------------- %
        
        function [A,B,C,D] = get_model_linear_3d(obj)
            g = 9.81;
            C_21 = (obj.m_b + 2*obj.m_w + 2*obj.I_wheels/obj.r_w^2) * obj.m_b * obj.l_cg;
            V_1  = (obj.m_b+2*obj.m_w+2*obj.I_wheels/(obj.r_w^2))*(obj.I_y+obj.m_b*obj.l_cg^2)-obj.m_b^2*obj.l_cg^2*cos(0)^2;
            D_22 = (obj.m_b+2*obj.m_w+2*obj.I_wheels/obj.r_w^2)*2*obj.c_alpha+obj.m_b*obj.l_cg*cos(0)*2*obj.c_alpha/obj.r_w;
            D_21 = (obj.m_b + 2*obj.m_w+2*obj.I_wheels/obj.r_w^2)*2*obj.c_alpha/obj.r_w+obj.m_b*obj.l_cg*cos(0)*2*obj.c_alpha/obj.r_w^2;
            C_11 = obj.m_b^2*obj.l_cg^2*cos(0);
            D_12 = (obj.I_y + obj.m_b * obj.l_cg^2)*2*obj.c_alpha/obj.r_w - obj.m_b * obj.l_cg * cos(0) * 2 * obj.c_alpha;
            D_11 = (obj.I_y + obj.m_b * obj.l_cg^2)*2*obj.c_alpha/obj.r_w^2 - obj.m_b * obj.l_cg * cos(0)*2*obj.c_alpha/obj.r_w;
            D_33 = obj.d_wheels / (2*obj.r_w^2) * obj.c_alpha;
            V_2 = obj.I_z + 2*obj.I_wheels + (obj.m_w + obj.I_wheels/(obj.r_w^2)) * obj.d_wheels^2/2;
            
            
            A = [   0           1           0           0           0           0;
                0           -D_11/V_1   -C_11*g/V_1 D_12/V_1    0           0;
                0           0           0           1           0           0;
                0           D_21/V_1    C_21*g/V_1  -D_22/V_1   0           0;
                0           0           0           0           0           1;
                0           0           0           0           0           -D_33/V_2];
            
            
            B_2 = obj.m_b*obj.l_cg/obj.r_w*cos(0)+obj.m_b+2*obj.m_w+2*obj.I_wheels/(obj.r_w^2);
            B_1 = (obj.I_y + obj.m_b*obj.l_cg^2)/obj.r_w+obj.m_b*obj.l_cg*cos(0);
            B_3 = obj.d_wheels / (2*obj.r_w);
            
            B = [   0           0;
                B_1/V_1     B_1/V_1;
                0           0;
                -B_2/V_1    -B_2/V_1;
                0           0;
                -B_3/V_2    B_3/V_2];
            
            
            
            C = [0 0 1 0 0 0];
            D = [0 0];
        end
        
        % --------------------------------------------------------------- %
        
        function [state_dot] = model_nonlinear(obj,u)
            g = 9.81;
            x           = obj.state(1);
            x_dot       = obj.state(2);
            theta       = obj.state(3);
            theta_dot   = obj.state(4);
            psi         = obj.state(5);
            psi_dot     = obj.state(6);
            
            
            C_12 = (obj.I_y+obj.m_b*obj.l_cg^2)*obj.m_b*obj.l_cg;
            C_22 = obj.m_b^2*obj.l_cg^2*cos(theta);
            C_21 = (obj.m_b + 2*obj.m_w + 2*obj.I_wheels/obj.r_w^2) * obj.m_b * obj.l_cg;
            V_1  = (obj.m_b+2*obj.m_w+2*obj.I_wheels/(obj.r_w^2))*(obj.I_y+obj.m_b*obj.l_cg^2)-obj.m_b^2*obj.l_cg^2*cos(theta)^2;
            D_22 = (obj.m_b+2*obj.m_w+2*obj.I_wheels/obj.r_w^2)*2*obj.c_alpha+obj.m_b*obj.l_cg*cos(theta)*2*obj.c_alpha/obj.r_w;
            D_21 = (obj.m_b + 2*obj.m_w+2*obj.I_wheels/obj.r_w^2)*2*obj.c_alpha/obj.r_w+obj.m_b*obj.l_cg*cos(theta)*2*obj.c_alpha/obj.r_w^2;
            C_11 = obj.m_b^2*obj.l_cg^2*cos(theta);
            D_12 = (obj.I_y + obj.m_b * obj.l_cg^2)*2*obj.c_alpha/obj.r_w - obj.m_b * obj.l_cg * cos(theta) * 2 * obj.c_alpha;
            D_11 = (obj.I_y + obj.m_b * obj.l_cg^2)*2*obj.c_alpha/obj.r_w^2 - obj.m_b * obj.l_cg * cos(theta)*2* obj.c_alpha/obj.r_w;
            B_2  = obj.m_b*obj.l_cg/obj.r_w*cos(theta)+obj.m_b+2*obj.m_w+2*obj.I_wheels/(obj.r_w^2);
            B_1  = (obj.I_y + obj.m_b*obj.l_cg^2)/obj.r_w+obj.m_b*obj.l_cg*cos(theta);
            
            C_31 = 2*(obj.I_z - obj.I_x - obj.m_b*obj.l_cg^2)*cos(theta);
            C_32 = obj.m_b * obj.l_cg;
            D_33 = obj.d_wheels^2 / (2*obj.r_w^2)*obj.c_alpha;
            V_2 = obj.I_z + 2*obj.I_wheels + (obj.m_w + obj.I_wheels / (obj.r_w^2)) * obj.d_wheels^2 / 2 - (obj.I_z - obj.I_x - obj.m_b*obj.l_cg^2)*sin(theta)^2;
            B_3 = obj.d_wheels / (2*obj.r_w);
            
            C_13 = (obj.I_y + obj.m_b*obj.l_cg^2)*obj.m_b*obj.l_cg + obj.m_b*obj.l_cg * (obj.I_z-obj.I_x-obj.m_b*obj.l_cg^2)*cos(theta)^2;
            C_23 = (obj.m_b^2*obj.l_cg^2+(obj.m_b+2*obj.m_w+2*obj.I_wheels/obj.r_w^2)*(obj.I_z-obj.I_x-obj.m_b*obj.l_cg^2))*cos(theta);
            
            state_dot = zeros(6,1);
            
            state_dot(1) = x_dot;
            state_dot(2) = sin(theta)/V_1 * (-C_11*g+C_12*theta_dot^2 + C_13*psi_dot^2) - D_11/V_1 * x_dot + D_12/V_1 * theta_dot + B_1/V_1 * (u(1) + u(2))-obj.tau_x*state_dot(1);
            state_dot(3) = theta_dot;
            state_dot(4) = sin(theta)/V_1 * (C_21*g-C_22*theta_dot^2 - C_23 * psi_dot^2) + D_21/V_1 * x_dot - D_22/V_1 * theta_dot - B_2/V_1 * (u(1) + u(2))-obj.tau_theta*state_dot(3);
            state_dot(5) = psi_dot;
            state_dot(6) = sin(theta)/V_2 * (C_31 * theta_dot * psi_dot - C_32 * psi_dot * x_dot) - D_33/V_2 * psi_dot - B_3/V_2 * (u(1) - u(2));
        end
        
        % --------------------------------------------------------------- %
        
        function u = controller(obj,u,mode)
            if(obj.ref_ctrl_is_set)
                u = obj.reference_controller(u);
            end
            if strcmp(mode,'linear')
                u = u - obj.K_discrete * obj.state;
            elseif strcmp(mode,'nonlinear')
                u = u - obj.K_cont * obj.state;
            end
        end
        
        % --------------------------------------------------------------- %
        
        function u = reference_controller(obj,w)
            
            % pitch
            
            e_pitch = w(1) - obj.state(obj.pitch_ref_ctrl_num);
            u_pitch = obj.P_pitch * e_pitch + obj.I_pitch * obj.integral_pitch + obj.D_pitch * 1/obj.Ts * (e_pitch-obj.last_error_pitch);
            
            if (abs(obj.I_pitch)>0)
                obj.integral_pitch = obj.integral_pitch + obj.Ts * e_pitch;
            end
            if(abs(obj.D_pitch)>0)
                obj.last_error_pitch = e_pitch;
            end
            
            % yaw
            
            e_yaw = w(2) - obj.state(obj.yaw_ref_ctrl_num);
            u_yaw = obj.P_yaw * e_yaw + obj.I_yaw * obj.integral_yaw + obj.D_yaw * 1/obj.Ts * (e_yaw-obj.last_error_yaw);
            
            if (abs(obj.I_yaw)>0)
                obj.integral_yaw = obj.integral_yaw + obj.Ts * e_yaw;
            end
            if(abs(obj.D_yaw)>0)
                obj.last_error_yaw = e_yaw;
            end
            
            u = [u_pitch + u_yaw;u_pitch - u_yaw];
            
        end
        
        % --------------------------------------------------------------- %
        
        function [y,x] = simulate_step_linear(obj,w)
            u = obj.controller(w,'linear');
            obj.state = obj.A_d*obj.state + obj.B_d*u;
            x = obj.state;
            y = obj.C*obj.state;
        end
        
        % --------------------------------------------------------------- %
        
        function [y,x] = simulate_step_nonlinear(obj,w)
            u = obj.controller(w,'nonlinear');
            x_dot = obj.model_nonlinear(u);
            obj.state = obj.state + obj.Ts*x_dot;
            x = obj.state;
            y = obj.C*obj.state;
        end
        
        % --------------------------------------------------------------- %
        
        function [y_out,x_out] = simulate_linear_model(obj,u)
            N = size(u,2);
            x_out = zeros(6,N);
            y_out = zeros(1,N);
            x_out(:,1) = obj.state;
            y_out(:,1) = obj.C*obj.state;
            for k = 2:N
                [y_out(:,k),x_out(:,k)] = obj.simulate_step_linear(u(:,k-1));
            end
        end
        
        % --------------------------------------------------------------- %
        
        function [y_out,x_out] = simulate_nonlinear_model(obj,u)
            N = size(u,2);
            x_out = zeros(6,N);
            y_out = zeros(1,N);
            x_out(:,1) = obj.state;
            y_out(:,1) = obj.C*obj.state;
            for k = 2:N
                [y_out(:,k),x_out(:,k)] = obj.simulate_step_nonlinear(u(:,k-1));
            end
        end
    end
end
