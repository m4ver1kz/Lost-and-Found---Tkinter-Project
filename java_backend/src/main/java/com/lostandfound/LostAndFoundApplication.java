package com.lostandfound;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main application entry point for the Lost and Found Management System Backend.
 *
 * Exposes a local REST API over HTTP with JSON payloads, interfacing with
 * MySQL via JDBC to serve requests from the Python Tkinter desktop GUI.
 */
@SpringBootApplication
public class LostAndFoundApplication {

    public static void main(String[] args) {
        SpringApplication.run(LostAndFoundApplication.class, args);
    }
}
