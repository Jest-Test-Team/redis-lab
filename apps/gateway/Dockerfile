FROM golang:1.21-alpine AS build
WORKDIR /app
COPY apps/gateway/ ./
RUN go mod tidy && go build -o main .

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
WORKDIR /app
COPY --from=build /app/main .
EXPOSE 8080
CMD ["./main"]
