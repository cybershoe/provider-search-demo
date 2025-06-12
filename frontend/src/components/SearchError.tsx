export interface SearchErrorProps {
    message: string,
    className?: string
}

export function SearchError({ message, className = "" }: SearchErrorProps) {
    return (
        <div
            className={className}
            style={{ display: message ? "block" : "none" }}
        >
            <p>{message}</p>
        </div>
    )
}