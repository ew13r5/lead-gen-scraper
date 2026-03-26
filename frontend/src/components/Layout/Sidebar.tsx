import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/tasks/new", label: "New Task" },
  { to: "/results", label: "Results" },
  { to: "/settings", label: "Settings" },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-20 md:hidden"
          onClick={onClose}
          data-testid="sidebar-overlay"
        />
      )}
      <aside
        className={`fixed top-0 left-0 z-30 h-full w-60 bg-white border-r border-gray-200 transform transition-transform md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        data-testid="sidebar"
      >
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-lg font-bold text-gray-900">Lead Gen Scraper</h1>
        </div>
        <nav className="mt-4 flex flex-col gap-1 px-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              onClick={onClose}
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-gray-200 font-semibold text-gray-900"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
