package com.recapify.llm;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

    @Test
    void mapsContentUnavailableExceptionToHttp404WithUserMessage() {
        ContentUnavailableException ex = new ContentUnavailableException("Breaking Bad", 99, 99, "en");

        ResponseEntity<Map<String, String>> response = handler.handleContentUnavailable(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
        assertThat(response.getBody()).containsEntry("error", "content_unavailable");
        assertThat(response.getBody().get("message"))
                .contains("Breaking Bad")
                .contains("99")
                .contains("Did we understand your request correctly?");
    }

    @Test
    void mapsMlServiceUnavailableExceptionToHttp503WithUserMessage() {
        MlServiceUnavailableException ex = new MlServiceUnavailableException("ML service down");

        ResponseEntity<Map<String, String>> response = handler.handleMlServiceUnavailable(ex);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.SERVICE_UNAVAILABLE);
        assertThat(response.getBody()).containsEntry("error", "service_unavailable");
        assertThat(response.getBody().get("message")).contains("Please try again");
    }
}
