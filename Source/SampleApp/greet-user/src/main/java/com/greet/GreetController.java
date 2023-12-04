package com.greet;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetController {
	
	private static final String template = "Hello, %s!";
	private final AtomicLong counter = new AtomicLong();
	
	@RequestMapping("/hello")
	public Greet sayHi(@RequestParam(value = "name", defaultValue = "World") String name) { 
		//Spring MVC converts List into JSON
		
		System.out.print("/hello called with param: " );
		if(name.equalsIgnoreCase("World"))
			System.out.println("World (Default)");
		else
			System.out.println(name);
		return new Greet(counter.incrementAndGet(), String.format(template, name));
	}

}
