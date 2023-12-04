package com.greet;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

@SpringBootApplication 
public class Runner {

	public static void main(String[] args) {
		
		SpringApplication.run(Runner.class, args);
		System.out.println("----Console Logs----");
		System.out.println("Server started on port: 8080");
		System.out.println("Status: 200 OK");
		
	}

}
