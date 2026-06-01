package com.recapify.logging;

import jakarta.servlet.ServletException;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import java.io.IOException;

import static org.assertj.core.api.Assertions.assertThat;

class RequestLoggingFilterTest {

    private final RequestLoggingFilter filter = new RequestLoggingFilter();

    @Test
    void skipsNonApiRequests() throws ServletException, IOException {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, (servletRequest, servletResponse) ->
                assertThat(MDC.get("requestId")).isNull()
        );

        assertThat(response.getHeader("X-Request-Id")).isNull();
    }

    @Test
    void preservesIncomingRequestIdAndClearsMdc() throws ServletException, IOException {
        String requestId = "request-123";
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/llm/summary");
        MockHttpServletResponse response = new MockHttpServletResponse();
        request.addHeader("X-Request-Id", requestId);

        filter.doFilter(request, response, (servletRequest, servletResponse) ->
                assertThat(MDC.get("requestId")).isEqualTo(requestId)
        );

        assertThat(response.getHeader("X-Request-Id")).isEqualTo(requestId);
        assertThat(MDC.get("requestId")).isNull();
    }

    @Test
    void generatesRequestIdWhenMissingAndClearsMdc() throws ServletException, IOException {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/llm/summary");
        MockHttpServletResponse response = new MockHttpServletResponse();

        filter.doFilter(request, response, (servletRequest, servletResponse) ->
                assertThat(MDC.get("requestId")).isNotBlank()
        );

        assertThat(response.getHeader("X-Request-Id")).isNotBlank();
        assertThat(MDC.get("requestId")).isNull();
    }
}
