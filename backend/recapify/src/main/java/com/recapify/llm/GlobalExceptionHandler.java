package com.recapify.llm;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ContentUnavailableException.class)
    ResponseEntity<Map<String, String>> handleContentUnavailable(ContentUnavailableException e) {
        String message = String.format(
                "We couldn't find content for %s Season %s Episode %s. Did we understand your request correctly?",
                e.title(),
                e.season() != null ? e.season() : "?",
                e.episode() != null ? e.episode() : "?"
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(Map.of("error", "content_unavailable", "message", message));
    }

    @ExceptionHandler(MlServiceUnavailableException.class)
    ResponseEntity<Map<String, String>> handleMlServiceUnavailable(MlServiceUnavailableException e) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "service_unavailable",
                        "message", "Something went wrong while generating the summary. Please try again."));
    }
}
