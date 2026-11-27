from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QFrame,
)

from app.core import show_error
from app.core.app_state import AppState
from app.core.exceptions import ValidationError

from .service import AnalysisService
from .views.forecast_view import ForecastView
from .views.trends_view import TrendsView
from .widgets.tab_bar import TabBar

from app.features.wallets.service import WalletService
from app.features.wallets.widgets.wallet_form_dialog import WalletFormDialog

TRENDS = "trends"
FORECAST = "forecast"

# Tabs as data so the set can become wallet-type dependent later without
# touching the layout. Investment wallets will want a different list.
TABS = [
    (TRENDS, "Trends"),
    (FORECAST, "Forecast"),
]


class AnalysisView(QWidget):
    """Shell for the Analysis section: a wallet line, tabs, two pages.

    Owns nothing but the switch. Each page talks to AnalysisService on
    its own, so adding a third tab means adding a page and a tuple.

    Pages are built once here but only load on first show, because
    QStackedWidget does not send showEvent to a page nobody has opened.
    Opening Analysis therefore costs one query set, not two.
    """

    def __init__(
        self,
        service: AnalysisService,
        wallet_service: WalletService,
        app_state: AppState,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.service = service
        self.wallet_service = wallet_service
        self.app_state = app_state

        self._init_view()

        self.app_state.wallet_changed.connect(self._update_wallet_label)
        self._update_wallet_label()

    def _init_view(self):
        "Initialize view"
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self._build_header())
        main_layout.addWidget(self._build_pages())

    def _build_header(self) -> QWidget:
        """Page title, the wallet these numbers are about, and the tabs.

        The wallet is the part the reader cannot infer, and every figure on
        both pages is scoped to it - so it sits right under the title. The
        tabs hang from the bottom edge so their underline lands on the
        header's border.
        """
        header = QFrame(self)
        header.setObjectName("analysisHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 16, 5, 0)
        header_layout.setSpacing(14)

        titles = QWidget(header)
        titles_layout = QVBoxLayout(titles)
        titles_layout.setContentsMargins(0, 0, 0, 12)
        titles_layout.setSpacing(2)

        self.title_label = QLabel("Analysis", titles)
        self.title_label.setObjectName("analysisTitle")

        self.wallet_label = QLabel(titles)
        self.wallet_label.setObjectName("analysisWalletLabel")

        titles_layout.addWidget(self.title_label)
        titles_layout.addWidget(self.wallet_label)

        self.tabs = TabBar(
            parent=header,
            values=TABS,
            default_value=TRENDS,
            on_change=self._on_tab_changed,
        )
        self.tabs.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        header_layout.addWidget(titles)
        header_layout.addStretch()
        header_layout.addWidget(self.tabs, alignment=Qt.AlignmentFlag.AlignBottom)

        return header

    def _build_pages(self) -> QWidget:
        self.trends_view = TrendsView(
            service=self.service, app_state=self.app_state, parent=self
        )
        self.forecast_view = ForecastView(
            service=self.service, app_state=self.app_state, parent=self
        )
        self.forecast_view.edit_assumptions_requested.connect(self._edit_assumptions)

        self.stacked_pages = QStackedWidget(self)
        self.stacked_pages.addWidget(self.trends_view)
        self.stacked_pages.addWidget(self.forecast_view)

        self._pages = {TRENDS: self.trends_view, FORECAST: self.forecast_view}

        return self.stacked_pages

    # EVENTS
    def _on_tab_changed(self, tab: str):
        page = self._pages.get(tab)
        if page is not None:
            self.stacked_pages.setCurrentWidget(page)

    def _update_wallet_label(self, wallet_id: int = None):
        wallet = self._active_wallet()
        if wallet is None:
            self.wallet_label.setText("No wallet selected")
            return

        self.wallet_label.setText(f"{wallet.name} · {wallet.currency}")

    def _edit_assumptions(self):
        """Open the wallet so the plan can be changed.

        Analysis does not own these fields, so it hands off to the dialog
        that does rather than growing a second editor for them. The
        dialog's save emits wallet_changed, which both pages already
        listen to.
        """
        wallet = self._active_wallet()
        if wallet is None:
            show_error(
                self,
                "Select a wallet before editing its plan.",
                title="No wallet",
            )
            return

        try:
            dialog = WalletFormDialog(
                service=self.wallet_service, wallet=wallet, parent=self
            )
        except ValidationError as error:
            show_error(self, str(error))
            return

        dialog.exec()

    def _active_wallet(self):
        wallet_id = self.app_state.active_wallet_id
        if wallet_id is None:
            return None
        return self.wallet_service.get_wallet(wallet_id=wallet_id)
