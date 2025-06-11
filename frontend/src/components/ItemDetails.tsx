import ReactModal from 'react-modal';
import { ProviderItem

 } from './SuggestionList';
export interface ItemDetailsProps {
    data: ProviderItem,
    visible: boolean,
    onClose?: () => void,
    className?: string,
}

export function ItemDetails({
        data,
        visible,
        onClose= () => {},
        className="",
    }: ItemDetailsProps) {

    console.log(JSON.stringify(data))

    const { score, scoreDetails, ...responseData } = data ? data : { score: 1, scoreDetails: {}}

    return (
        <ReactModal
            isOpen={visible}
            appElement={document.getElementById("app") as HTMLElement}
            onRequestClose={onClose}
            className={className}
            shouldCloseOnEsc={true}
            shouldCloseOnOverlayClick={true}
        >
            <div onClick={onClose} className="itemDetailsContainer">
                <div className="itemDetailsSection">
                    <div className="itemDetailsHeading">
                        <h3>Result</h3>
                    </div>
                    <div className="itemDetailsContent">
                        <pre>{JSON.stringify(responseData, null, 2)}</pre>
                    </div>
                </div>
                <div className="itemDetailsSection">
                    <div className="itemDetailsHeading">
                        <h3>Search Statistics</h3>
                    </div>
                    <div className="itemDetailsContent">
                        <pre>{scoreDetails ? JSON.stringify(scoreDetails, null, 2) : `Score: ${score}`}</pre>
                    </div>
                </div>
            </div>
        </ReactModal>
    )
}