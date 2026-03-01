import { render, screen } from "@testing-library/react";
import { StatusBadge } from "@/components/ui/StatusBadge";

describe("StatusBadge", () => {
  it("renders connected label when connected", () => {
    render(<StatusBadge connected={true} label="已連線" />);
    expect(screen.getByText("已連線")).toBeInTheDocument();
  });

  it("renders disconnected label when not connected", () => {
    render(<StatusBadge connected={false} label="未連線" />);
    expect(screen.getByText("未連線")).toBeInTheDocument();
  });
});
