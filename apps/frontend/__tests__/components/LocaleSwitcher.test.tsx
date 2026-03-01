import { render, screen, fireEvent } from "@testing-library/react";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { LocaleProvider } from "@/contexts/LocaleContext";

function renderWithProvider() {
  return render(
    <LocaleProvider>
      <LocaleSwitcher />
    </LocaleProvider>
  );
}

describe("LocaleSwitcher", () => {
  it("renders 繁中 and EN buttons", () => {
    renderWithProvider();
    expect(screen.getByText("繁中")).toBeInTheDocument();
    expect(screen.getByText("EN")).toBeInTheDocument();
  });

  it("calls setLocale when 繁中 is clicked", () => {
    renderWithProvider();
    fireEvent.click(screen.getByText("繁中"));
    expect(document.documentElement.lang).toBe("zh-TW");
  });

  it("calls setLocale when EN is clicked", () => {
    renderWithProvider();
    fireEvent.click(screen.getByText("EN"));
    expect(document.documentElement.lang).toBe("en");
  });
});
