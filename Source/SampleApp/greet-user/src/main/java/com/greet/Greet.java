package com.greet;

// component class - prototype can be used
public class Greet {

	private long id;
	private String content;
	
	
	public Greet(long id, String content) {
		super();
		this.id = id;
		this.content = content;
	}
	public long getId() {
		return id;
	}

	public String getContent() {
		return content;
	}

}

