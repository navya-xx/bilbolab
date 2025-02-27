/*
 * core_control_StateFeedback.h
 *
 *  Created on: 9 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_CONTROL_STATE_FEEDBACK_CORE_CONTROL_STATEFEEDBACK_H_
#define CORE_CONTROL_STATE_FEEDBACK_CORE_CONTROL_STATEFEEDBACK_H_


template <int states, int inputs>
class core_control_StateFeedback {

public:


	void update(float* state, float* input);
	float K[states][inputs] = {0};
private:

};


#endif /* CORE_CONTROL_STATE_FEEDBACK_CORE_CONTROL_STATEFEEDBACK_H_ */
