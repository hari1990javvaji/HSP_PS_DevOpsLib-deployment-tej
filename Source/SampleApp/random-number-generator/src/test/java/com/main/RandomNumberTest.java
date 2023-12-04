package com.main;

import org.springframework.boot.test.context.SpringBootTest;


import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
public class RandomNumberTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	public void noParamGreetingShouldReturnDefaultMessage() throws Exception {

		this.mockMvc.perform(get("/generate")).andDo(print())
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.name").value("Null"));
	}

	@Test
	public void paramGreetingShouldReturnTailoredMessage1() throws Exception {

		this.mockMvc.perform(get("/generate").param("name", "Anaghesh"))
				.andDo(print())
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.name").value("Anaghesh"));
	}
	@Test
	public void paramGreetingShouldReturnTailoredMessage2() throws Exception {

		this.mockMvc.perform(get("/generate").param("name", "123123"))
				.andDo(print())
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.name").value("123123"));
	}
	@Test
	public void paramGreetingShouldReturnTailoredMessage3() throws Exception {

		this.mockMvc.perform(get("/generate").param("name", "User123"))
				.andDo(print())
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.name").value("User123"));
	}
}
