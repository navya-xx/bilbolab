/*
 * core_utils_Callback.h
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_UTILS_CALLBACK_H_
#define CORE_UTILS_CORE_UTILS_CALLBACK_H_

#include "stdint.h"
#include "core_utils_functionpointer.h"

class Callback {
public:
	Callback() {

	}

	virtual void call() {

	}

	virtual void call(void *argument) {

	}
private:

};

template<typename output_type, typename input_type>
class core_utils_Callback: public Callback {
public:
	core_utils_Callback() {
		this->registered = 0;
	}

	core_utils_Callback(output_type (*function)(input_type)) {
		function_pointer = core_utils_FunctionPointer<output_type, input_type>(
				function);
		this->registered = 1;
	}

	template<typename cls>
	core_utils_Callback(cls *object, output_type (cls::*member)(input_type)) {
		function_pointer = core_utils_FunctionPointer<output_type, input_type>(
				object, member);
		this->registered = 1;
	}

	void set(output_type (*function)(input_type)) {
		this->function_pointer = core_utils_FunctionPointer<output_type,
				input_type>(function);
		this->registered = 1;
	}

	template<typename cls>
	void set(cls *object, output_type (cls::*member)(input_type)) {
		this->function_pointer = core_utils_FunctionPointer<output_type,
				input_type>(object, member);
		this->registered = 1;
	}

	void call(input_type argument, output_type &output) {
		output = this->function_pointer(argument);
	}

	bool operator==(const core_utils_Callback &other) const {
		return this->_fp == other._fp;
	}
//
	void operator()(void *argument) {
		return this->call(argument);
	}
//
//	void operator()() {
//		return this->call();
//	}

	uint8_t registered = 0;
private:
	core_utils_FunctionPointer<output_type, input_type> function_pointer;
};

template<typename output_type>
class core_utils_Callback<output_type, void> : public Callback {
public:
	core_utils_Callback() {
		this->registered = 0;
	}
	core_utils_Callback(output_type (*function)(void)) {
		_fp = core_utils_FunctionPointer<output_type, void>(function);
		this->registered = 1;
	}

	template<typename cls>
	core_utils_Callback(cls *object, output_type (cls::*member)(void)) {
		_fp = core_utils_FunctionPointer<output_type, void>(object, member);
		this->registered = 1;
	}

	void set(output_type (*function)(void)) {
		this->_fp = core_utils_FunctionPointer<output_type, void>(function);
		this->registered = 1;
	}

	template<typename cls>
	void set(cls *object, output_type (cls::*member)(void)) {
		this->_fp = core_utils_FunctionPointer<output_type, void>(object,
				member);
		this->registered = 1;
	}

	void call(output_type &output) {
		output = this->_fp();
	}
	bool operator==(const core_utils_Callback &other) const {
		return this->_fp == other._fp;
	}
//
//	void operator()(void *argument) {
//		return this->call(argument);
//	}
//
//	void operator()() {
//		return this->call();
//	}

	uint8_t registered = 0;
private:
	core_utils_FunctionPointer<output_type, void> _fp;
};

template<typename input_type>
class core_utils_Callback<void, input_type> : public Callback {
public:
	core_utils_Callback() {
		this->registered = 0;
	}
	core_utils_Callback(void (*function)(input_type)) {
		_fp = core_utils_FunctionPointer<void, input_type>(function);
		this->registered = 1;
	}

	template<typename cls>
	core_utils_Callback(cls *object, void (cls::*member)(input_type)) {
		_fp = core_utils_FunctionPointer<void, input_type>(object, member);
		this->registered = 1;
	}

	void set(void (*function)(input_type)) {
		this->_fp = core_utils_FunctionPointer<void, input_type>(function);
		this->registered = 1;
	}

	template<typename cls>
	void set(cls *object, void (cls::*member)(input_type)) {
		this->_fp = core_utils_FunctionPointer<void, input_type>(object,
				member);
		this->registered = 1;
	}

	void call(input_type input) {
		this->_fp(input);
	}
	bool operator==(const core_utils_Callback &other) const {
		return this->_fp == other._fp;
	}
//
//	void operator()(void *argument) {
//		return this->call(argument);
//	}
//
//	void operator()() {
//		return this->call();
//	}

	uint8_t registered = 0;
private:
	core_utils_FunctionPointer<void, input_type> _fp;
};

template<>
class core_utils_Callback<void, void> : public Callback {
public:
	core_utils_Callback() {
		this->registered = 0;
	}
	core_utils_Callback(void (*function)(void)) {
		_fp = core_utils_FunctionPointer<void, void>(function);
		this->registered = 1;
	}

	template<typename cls>
	core_utils_Callback(cls *object, void (cls::*member)(void)) {
		_fp = core_utils_FunctionPointer<void, void>(object, member);
		this->registered = 1;
	}

	void set(void (*function)(void)) {
		this->_fp = core_utils_FunctionPointer<void, void>(function);
		this->registered = 1;
	}

	template<typename cls>
	void set(cls *object, void (cls::*member)(void)) {
		this->_fp = core_utils_FunctionPointer<void, void>(object, member);
		this->registered = 1;
	}

	void call() {
		this->_fp();
	}
	bool operator==(const core_utils_Callback &other) const {
		return this->_fp == other._fp;
	}
//
//	void operator()(void *argument) {
//		return this->call(argument);
//	}
//
//	void operator()() {
//		return this->call();
//	}

	uint8_t registered = 0;
private:
	core_utils_FunctionPointer<void, void> _fp;
};

template<int num_callbacks, typename input_type>
class core_utils_CallbackContainer {
public:
	core_utils_CallbackContainer() {

	}

	bool registerFunction(void (*function)(input_type)) {
		if (this->callback_index < num_callbacks) {
			this->callbacks[this->callback_index].set(function);
			this->callback_index++;
			return true;
		} else {
			return false;
		}

	}

	template<typename cls>
	bool registerFunction(cls *object, void (cls::*member)(input_type)) {
		if (this->callback_index < num_callbacks) {
			this->callbacks[this->callback_index].set(object, member);
			this->callback_index++;
			return true;
		} else {
			return false;
		}
	}

	void call(input_type input) {
		for (int i = 0; i < num_callbacks; i++) {
			if (this->callbacks[i].registered) {
				this->callbacks[i].call(input);
			}
		}
	}

	int callback_index = 0;
	core_utils_Callback<void, input_type> callbacks[num_callbacks];
private:

};

template<int num_callbacks>
class core_utils_CallbackContainer<num_callbacks, void> {
public:
	core_utils_CallbackContainer() {

	}

	bool registerFunction(void (*function)(void)) {
		if (this->callback_index < num_callbacks) {
			this->callbacks[this->callback_index].set(function);
			this->callback_index++;
			return true;
		} else {
			return false;
		}

	}

	template<typename cls>
	bool registerFunction(cls *object, void (cls::*member)(void)) {
		if (this->callback_index < num_callbacks) {
			this->callbacks[this->callback_index].set(object, member);
			this->callback_index++;
			return true;
		} else {
			return false;
		}
	}

	void call() {
		for (int i = 0; i < num_callbacks; i++) {
			if (this->callbacks[i].registered) {
				this->callbacks[i].call();
			}
		}
	}

	int callback_index = 0;
	core_utils_Callback<void, void> callbacks[num_callbacks];
private:

};

#endif /* CORE_UTILS_CORE_UTILS_CALLBACK_H_ */
