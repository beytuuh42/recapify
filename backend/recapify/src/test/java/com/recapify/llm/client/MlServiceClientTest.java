package com.recapify.llm.client;

import com.recapify.llm.ContentUnavailableException;
import com.recapify.llm.MlServiceUnavailableException;
import com.recapify.llm.dto.SummaryRequest;
import com.recapify.llm.dto.SummaryResponse;
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
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class MlServiceClientTest {

    @AfterEach
    void tearDown() {
        MDC.clear();
    }

    @Test
    void extractsIntentFromMlService() {
        String prompt = "summarize Breaking Bad season 1 episode 1";
        String intentJson = """
                {"title":"Breaking Bad","media_type":"series","season":1,"episode":1,"language":"en"}
                """;
        SummaryRequest expectedIntent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(HttpStatus.OK, intentJson);
        MlServiceClient client = new MlServiceClient(WebClient.builder().exchangeFunction(exchange).build());

        SummaryRequest intent = client.extractIntent(prompt);

        ClientRequest request = exchange.requests().getFirst();
        assertThat(intent).isEqualTo(expectedIntent);
        assertThat(exchange.requests()).hasSize(1);
        assertThat(request.method().name()).isEqualTo("POST");
        assertThat(request.url().getPath()).isEqualTo("/api/v1/intent");
        assertThat(request.url().getQuery()).isEqualTo("message=summarize Breaking Bad season 1 episode 1");
    }

    @Test
    void fetchesSummaryAndPropagatesRequestId() {
        String requestId = "request-123";
        String summaryJson = """
                {"title":"Pilot","final_summary":"Walter starts cooking meth.","key_events":[],"characters":[],"chunk_summaries":[]}
                """;
        SummaryRequest intent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        SummaryResponse expectedSummary = new SummaryResponse("Pilot", "Walter starts cooking meth.", List.of(), List.of(), List.of());
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(HttpStatus.OK, summaryJson);
        MlServiceClient client = new MlServiceClient(WebClient.builder().exchangeFunction(exchange).build());
        MDC.put("requestId", requestId);

        SummaryResponse summary = client.fetchSummary(intent);

        ClientRequest summaryRequest = exchange.requests().getFirst();
        assertThat(summary).isEqualTo(expectedSummary);
        assertThat(exchange.requests()).hasSize(1);
        assertThat(summaryRequest.headers().getFirst("X-Request-Id")).isEqualTo(requestId);
        assertThat(summaryRequest.method().name()).isEqualTo("POST");
        assertThat(summaryRequest.url().getPath()).isEqualTo("/api/v1/summarize");
    }

    @Test
    void fetchSummaryThrowsContentUnavailableExceptionOnMl404WithSubtitleNotFound() {
        String errorBody = """
                {"detail":{"code":"subtitle_not_found","title":"Breaking Bad","season":99,"episode":99,"language":"en"}}
                """;
        SummaryRequest intent = new SummaryRequest("Breaking Bad", "series", 99, 99, "en");
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(HttpStatus.NOT_FOUND, errorBody);
        MlServiceClient client = new MlServiceClient(WebClient.builder().exchangeFunction(exchange).build());

        assertThatThrownBy(() -> client.fetchSummary(intent))
                .isInstanceOf(ContentUnavailableException.class)
                .satisfies(ex -> {
                    ContentUnavailableException e = (ContentUnavailableException) ex;
                    assertThat(e.title()).isEqualTo("Breaking Bad");
                    assertThat(e.season()).isEqualTo(99);
                    assertThat(e.episode()).isEqualTo(99);
                    assertThat(e.language()).isEqualTo("en");
                });
    }

    @Test
    void fetchSummaryThrowsMlServiceUnavailableExceptionOnMl503() {
        SummaryRequest intent = new SummaryRequest("Breaking Bad", "series", 1, 1, "en");
        RecordingExchangeFunction exchange = new RecordingExchangeFunction(HttpStatus.SERVICE_UNAVAILABLE, "");
        MlServiceClient client = new MlServiceClient(WebClient.builder().exchangeFunction(exchange).build());

        assertThatThrownBy(() -> client.fetchSummary(intent))
                .isInstanceOf(MlServiceUnavailableException.class);
    }

    private static final class RecordingExchangeFunction implements ExchangeFunction {
        private final HttpStatus status;
        private final String responseBody;
        private final List<ClientRequest> requests = new ArrayList<>();

        RecordingExchangeFunction(HttpStatus status, String responseBody) {
            this.status = status;
            this.responseBody = responseBody;
        }

        List<ClientRequest> requests() {
            return requests;
        }

        @Override
        public Mono<ClientResponse> exchange(ClientRequest request) {
            requests.add(request);
            return Mono.just(ClientResponse.create(status)
                    .header("Content-Type", "application/json")
                    .body(responseBody)
                    .build());
        }
    }
}
