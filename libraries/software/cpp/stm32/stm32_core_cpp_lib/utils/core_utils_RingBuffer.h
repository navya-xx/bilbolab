/*
 * core_utils_RingBuffer.h
 *
 *  Created on: Jul 29, 2022
 *      Author: Dustin Lehmann
 */

#ifndef UTILS_CORE_UTILS_RINGBUFFER_H_
#define UTILS_CORE_UTILS_RINGBUFFER_H_

template<int size>
class core_utils_RingBuffer {
public:

	core_utils_RingBuffer() {

	}

	void clear() {
		this->start = 0;
		this->end = 0;
		this->available = 0;
		this->overflow = false;
	}

	void add(uint8_t u8Val) {

		this->buffer[this->end] = u8Val;
		this->end = (this->end + 1) % size;
		if (this->available == size) {
			this->overflow = true;
			this->start = (this->start + 1) % size;
		} else {
			this->overflow = false;
			this->available++;
		}

	}

	uint8_t get_n_bytes(uint8_t *buffer, uint8_t number) {
		uint8_t uCounter;
		if (this->available == 0 || number == 0)
			return 0;
		if (number > size)
			return 0;

		for (uCounter = 0; uCounter < number && uCounter < this->available;
				uCounter++) {
			buffer[uCounter] = this->buffer[this->start];
			this->start = (this->start + 1) % size;
		}
		this->available = this->available - uCounter;
		this->overflow = false;
		this->clear();

		return uCounter;
	}

	uint8_t get_all_bytes(uint8_t *buffer) {
		return this->get_n_bytes(buffer, this->available);
	}

	uint8_t count_bytes() {
		return this->available;
	}

	uint8_t buffer[size];
	uint8_t start;
	uint8_t end;
	uint8_t available;
	bool overflow;
private:

};

#endif /* UTILS_CORE_UTILS_RINGBUFFER_H_ */
