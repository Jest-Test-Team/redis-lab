FROM golang:1.21-alpine AS build
WORKDIR /app
COPY apps/sentinel/ ./
RUN go mod tidy && go build -o main .

FROM alpine:3.19
WORKDIR /app
COPY --from=build /app/main .
CMD ["./main"]
