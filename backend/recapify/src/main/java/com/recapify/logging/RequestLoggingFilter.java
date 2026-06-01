package com.recapify.logging;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

@Slf4j
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final String REQUEST_ID_HEADER = "X-Request-Id";
    private static final String REQUEST_ID_KEY = "requestId";

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith("/api/");
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        String requestId = getRequestId(request);
        long startedAt = System.nanoTime();

        MDC.put(REQUEST_ID_KEY, requestId);
        response.setHeader(REQUEST_ID_HEADER, requestId);

        try {
            log.info("Incoming request method={} path={}", request.getMethod(), request.getRequestURI());
            filterChain.doFilter(request, response);
        } finally {
            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.info(
                    "Completed request method={} path={} status={} durationMs={}",
                    request.getMethod(),
                    request.getRequestURI(),
                    response.getStatus(),
                    durationMs
            );
            MDC.remove(REQUEST_ID_KEY);
        }
    }

    private String getRequestId(HttpServletRequest request) {
        String requestId = request.getHeader(REQUEST_ID_HEADER);
        return requestId == null || requestId.isBlank() ? UUID.randomUUID().toString() : requestId;
    }
}
