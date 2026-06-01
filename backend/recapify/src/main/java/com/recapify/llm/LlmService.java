package com.recapify.llm;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Slf4j
@Service
@RequiredArgsConstructor
public class LlmService {

    private static final String REQUEST_ID_HEADER = "X-Request-Id";
    private static final String REQUEST_ID_KEY = "requestId";

    private final WebClient llmServiceWebClient;

    public SummaryRequest getIntent(String text) {
        long startedAt = System.nanoTime();
        IntentRequest req = new IntentRequest(text);

        try {
            log.info("Requesting intent from ML service textLength={}", text.length());
            SummaryRequest summaryRequest = llmServiceWebClient.post()
                    .uri(uriBuilder -> uriBuilder.path("/api/v1/intent").queryParam("message", req.message()).build())
                    .headers(this::addRequestIdHeader)
                    .retrieve()
                    .bodyToMono(SummaryRequest.class)
                    .block();

            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.info(
                    "Intent received from ML service title={} season={} episode={} language={} durationMs={}",
                    summaryRequest.title(),
                    summaryRequest.season(),
                    summaryRequest.episode(),
                    summaryRequest.language(),
                    durationMs
            );
            return summaryRequest;
        } catch (RuntimeException e) {
            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.error("Intent request to ML service failed durationMs={}", durationMs, e);
            throw e;
        }
    }

    public Summary getSummary(String text) {
        long startedAt = System.nanoTime();
        SummaryRequest summaryRequest = getIntent(text);

        try {
            log.info(
                    "Requesting episode summary from ML service title={} season={} episode={} language={}",
                    summaryRequest.title(),
                    summaryRequest.season(),
                    summaryRequest.episode(),
                    summaryRequest.language()
            );
            Summary summary = llmServiceWebClient.post()
                    .uri("/api/v1/summarize")
                    .headers(this::addRequestIdHeader)
                    .bodyValue(summaryRequest)
                    .retrieve()
                    .bodyToMono(SummaryResponse.class)
                    .map(res -> new Summary(res.final_summary()))
                    .block();

            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.info("Episode summary received from ML service summaryLength={} durationMs={}", summary.content().length(), durationMs);
            return summary;
        } catch (RuntimeException e) {
            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.error("Episode summary request to ML service failed durationMs={}", durationMs, e);
            throw e;
        }
    }

    private void addRequestIdHeader(HttpHeaders headers) {
        String requestId = MDC.get(REQUEST_ID_KEY);
        if (requestId != null && !requestId.isBlank()) {
            headers.set(REQUEST_ID_HEADER, requestId);
        }
    }
}
