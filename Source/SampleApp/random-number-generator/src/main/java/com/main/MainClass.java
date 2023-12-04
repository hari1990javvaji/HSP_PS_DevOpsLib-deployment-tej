package com.main;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication 
public class MainClass {

	public static void main(String[] args) {
		SpringApplication.run(MainClass.class, args);
		System.out.println("----Console Logs----");
		System.out.println("Server started on port: 8080");
		System.out.println("Status: 200 OK");

	}

}
