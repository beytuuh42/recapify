package com.recapify.llm;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientRequest;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.ExchangeFunction;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class LlmServiceTest {

    @AfterEach
    void tearDown() {
        MDC.clear();
    }

    @Test
    void requestsIntentFromMlService() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        String intentJson = """
                {"title":"Breaking Bad","media_type":"series","season":1,"episode":1,"language":"en"}
                """;
        SummaryRequest expectedIntent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(intentJson);
        LlmService service = new LlmService(WebClient.builder().exchangeFunction(exchange).build());

        SummaryRequest intent = service.getIntent(prompt);

        ClientRequest request = exchange.requests().getFirst();
        assertThat(intent).isEqualTo(expectedIntent);
        assertThat(exchange.requests()).hasSize(1);
        assertThat(request.method().name()).isEqualTo("POST");
        assertThat(request.url().getPath()).isEqualTo("/api/v1/intent");
        assertThat(request.url().getQuery()).isEqualTo("message=summarize Breaking Bad season 1 episode 1");
    }

    @Test
    void requestsSummaryFromMlServiceAndPropagatesRequestId() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        String requestId = "request-123";
        String intentJson = """
                {"title":"Breaking Bad","media_type":"series","season":1,"episode":1,"language":"en"}
                """;
        String summaryJson = """
                {"title":"Pilot","final_summary":"Walter starts cooking meth.","key_events":[],"characters":[],"chunk_summaries":[]}
                """;
        Summary expectedSummary = new Summary("Walter starts cooking meth.");
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(intentJson, summaryJson);
        LlmService service = new LlmService(WebClient.builder().exchangeFunction(exchange).build());
        MDC.put("requestId", requestId);

        Summary summary = service.getSummary(prompt);

        ClientRequest intentRequest = exchange.requests().get(0);
        ClientRequest summaryRequest = exchange.requests().get(1);
        assertThat(summary).isEqualTo(expectedSummary);
        assertThat(exchange.requests()).hasSize(2);
        assertThat(intentRequest.headers().getFirst("X-Request-Id")).isEqualTo(requestId);
        assertThat(summaryRequest.headers().getFirst("X-Request-Id")).isEqualTo(requestId);
        assertThat(summaryRequest.method().name()).isEqualTo("POST");
        assertThat(summaryRequest.url().getPath()).isEqualTo("/api/v1/summarize");
    }

    private static final class RecordingExchangeFunction implements ExchangeFunction {
        private final List<String> responses;
        private final List<ClientRequest> requests = new ArrayList<>();
        private int responseIndex = 0;

        RecordingExchangeFunction(String... responses) {
            this.responses = List.of(responses);
        }

        List<ClientRequest> requests() {
            return requests;
        }

        @Override
        public Mono<ClientResponse> exchange(ClientRequest request) {
            String responseBody = responses.get(responseIndex++);
            requests.add(request);
            return Mono.just(ClientResponse.create(HttpStatus.OK)
                    .header("Content-Type", "application/json")
                    .body(responseBody)
                    .build());
        }
    }
}
