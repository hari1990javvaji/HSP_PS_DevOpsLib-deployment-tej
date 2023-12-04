package com.main;

import java.util.Random;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RandomController {

	
	@RequestMapping("/generate")
	public RandomNumber generateNumber(@RequestParam(value = "name", defaultValue = "Null") String name){
		 Random rand = new Random(); 
		 int rand_int1 = rand.nextInt(100000); 
		return new RandomNumber(rand_int1, name );
	}
}