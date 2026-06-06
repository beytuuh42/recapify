package com.recapify.llm.client;

import com.recapify.llm.dto.IntentRequest;
import com.recapify.llm.dto.SummaryRequest;
import com.recapify.llm.dto.SummaryResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Slf4j
@Service
@RequiredArgsConstructor
public class MlServiceClient {

    private static final String REQUEST_ID_HEADER = "X-Request-Id";
    private static final String REQUEST_ID_KEY = "requestId";

    private final WebClient llmServiceWebClient;

    public SummaryRequest extractIntent(String text) {
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

    public SummaryResponse fetchSummary(SummaryRequest summaryRequest) {
        long startedAt = System.nanoTime();

        try {
            log.info(
                    "Requesting episode summary from ML service title={} season={} episode={} language={}",
                    summaryRequest.title(),
                    summaryRequest.season(),
                    summaryRequest.episode(),
                    summaryRequest.language()
            );
            SummaryResponse summary = llmServiceWebClient.post()
                    .uri("/api/v1/summarize")
                    .headers(this::addRequestIdHeader)
                    .bodyValue(summaryRequest)
                    .retrieve()
                    .bodyToMono(SummaryResponse.class)
                    .block();

            long durationMs = (System.nanoTime() - startedAt) / 1_000_000;
            log.info("Episode summary received from ML service finalSummaryLength={} keyEventsCount={} durationMs={}",
                    summary.final_summary().length(), summary.key_events().size(), durationMs);
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
